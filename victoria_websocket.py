import time
import random
import logging
import json
import asyncio
import queue
import functools
import multiprocessing
import avro
import avro.schema
import avro.io
import io
import itertools
import os
import websockets
import signal
import sys
from kafka import KafkaConsumer
from kafka.structs import TopicPartition

import anomalies

from cfg import cfg

log = logging.getLogger("flasktoria.ws")
log.setLevel(logging.INFO)

def parse_gps_message(msg, wsctl_dict):
    #value = json.loads(msg['value'])['value']
    value = msg['value'].split(': ')[1].replace('[', '').replace(']', '')
    vehicle = msg['uuid']
    #log.debug("msg: {}".format(msg))
    longlat_pair = value
    lat, longitude = longlat_pair.split(',')
    try:
        key = 'position#' + vehicle + '#'
        wsctl_dict[key]

        # if we didn't get a KeyError from the line above, then
        # this message is suppressed
        return
    except KeyError:
        # no key means this message is not suppressed
        return {
            "update_type": "position",
            "vehicle_id": vehicle,
            "lat": lat,
            "long": longitude
        }

def parse_sensor_update(msg, wsctl_dict):
    #value = json.loads(msg['value'])['value']
    value = msg['value'].split(': ')[1]
    vehicle_id = msg['uuid']
    sensor = msg['sensor']

    try:
        key = 'sensordata#' + vehicle_id + '#' + sensor
        wsctl_dict[key]

        # if we didn't get a KeyError from the line above, then
        # this message is suppressed
        return
    except KeyError:
        # no key means this message is not suppressed
        return {
            'update_type': 'sensordata',
            'vehicle_id': vehicle_id,
            'sensor_id': sensor,
            'value': value
        }

def parse_anomaly_message(msg):
    anomaly = anomalies.create_from_template(msg['anomaly_id'], msg['uuid'], msg['detection_time'], msg['confirmation_time'])

    if anomaly is not None:
        anomaly['update_type'] = 'anomaly'
        return anomaly
    else:
        log.warn("Could not find anomaly template for anomaly id %s", msg['anomaly_id'])

def parse_kafka_message(wsctl_dict, msg):
    if 'anomaly_id' in msg:
        # must be an anomaly update
        timestamp = msg['timestamp']
        return timestamp, parse_anomaly_message(msg)

    if 'sensor' in msg:
        # must be a sensor update
        timestamp = msg['timestamp']
        if msg['sensor'] == 'gps_coordinates':
            # gps messages have a different format and must be specially processed
            return timestamp, parse_gps_message(msg, wsctl_dict)
        else:
            return timestamp, parse_sensor_update(msg, wsctl_dict)

    log.warn("Got unparseable kafka message: %s", msg)

def get_kafka_updates(msg_queue):
    updates = []
    while True:
        try:
            updates.append(msg_queue.get(block=False))
        except queue.Empty:
            return updates


def get_sensor_consumer():
    topic = cfg("KAFKA_TOPIC")
    schema_path = cfg("AVRO_SCHEMA_PATH")
    bootstrap_server = cfg("KAFKA_BOOTSTRAP_SERVER")

    with open(schema_path) as fin:
        avro_schema = avro.schema.Parse(fin.read())

    log.debug("kafka bootstrap server: %s", bootstrap_server)
    consumer = KafkaConsumer(bootstrap_servers=[bootstrap_server], auto_offset_reset='latest', enable_auto_commit=False)
    consumer.assign([TopicPartition(topic=topic, partition=0)])
    return consumer

def get_anomaly_consumer():
    topic = cfg("KAFKA_ANOMALY_TOPIC")
    schema_path = cfg("AVRO_ANOMALY_SCHEMA_PATH")
    bootstrap_server = cfg("KAFKA_BOOTSTRAP_SERVER")

    with open(schema_path) as fin:
        avro_schema = avro.schema.Parse(fin.read())

    log.debug("kafka bootstrap server: %s", bootstrap_server)
    consumer = KafkaConsumer(bootstrap_servers=[bootstrap_server], auto_offset_reset='latest', enable_auto_commit=False)
    consumer.assign([TopicPartition(topic=topic, partition=0)])
    return consumer

def deser_sensor_message(msg):
    schema_path = cfg("AVRO_SCHEMA_PATH")
    with open(schema_path) as fin:
        avro_schema = avro.schema.Parse(fin.read())
    try:
        bytes_reader = io.BytesIO(msg.value)
        decoder = avro.io.BinaryDecoder(bytes_reader)
        reader = avro.io.DatumReader(avro_schema)
        record = reader.read(decoder)
        #log.debug("Received anomaly message: {}".format(record))
        return record
    except AssertionError:
        log.warn("Got assertion error from avro decode on message: %s", msg)

def deser_anomaly_message(msg):
    schema_path = cfg("AVRO_ANOMALY_SCHEMA_PATH")
    with open(schema_path) as fin:
        avro_schema = avro.schema.Parse(fin.read())
    try:
        bytes_reader = io.BytesIO(msg.value)
        decoder = avro.io.BinaryDecoder(bytes_reader)
        reader = avro.io.DatumReader(avro_schema)
        record = reader.read(decoder)
        #log.debug("Received anomaly message: {}".format(record))
        return record
    except AssertionError:
        log.warn("Got assertion error from avro decode on message: %s", msg)

def ws_main(wsctl_dict):
    log.debug('in ws main (pid is %d)', os.getpid())

    def sigterm_handler(signum, frame):
        asyncio.get_event_loop().stop()
        log.debug("asyncio event loop stopped")
        log.info("Websocket server terminating")
        sys.exit(0)

    signal.signal(signal.SIGTERM, sigterm_handler)

    # read config to find host and port to set up ws server on
    _, _, port = cfg('WS_URL').split(':')
    host = "0.0.0.0"
    log.info('starting ws server on %s:%s', host, port)

    # define our emit loop as a closure so we can access wsctl_dict
    async def emit_loop(ws, path):
        log.info("New websocket connection established")

        running = True
        sensor_consumer = get_sensor_consumer()
        anomaly_consumer = get_anomaly_consumer()
        sensor_topic = cfg("KAFKA_TOPIC")
        anomaly_topic = cfg("KAFKA_ANOMALY_TOPIC")

        while running:
            sensor_records = sensor_consumer.poll(timeout_ms=250)
            topic_partition = TopicPartition(topic=sensor_topic, partition=0)
            if topic_partition in sensor_records:
                sensor_updates = map(deser_sensor_message, sensor_records[topic_partition])
                num_sensor_updates = len(sensor_records[topic_partition])
            else:
                log.debug('Missing key %s in sensor records poll dict, probably no messages arrived', sensor_topic)
                num_sensor_updates = 0
                sensor_updates = []

            anomaly_records = anomaly_consumer.poll(timeout_ms=250)
            topic_partition = TopicPartition(topic=anomaly_topic, partition=0)
            if len(anomaly_records) > 0:
                anomaly_updates = map(deser_anomaly_message, anomaly_records[topic_partition])
                num_anomaly_updates = len(anomaly_records[topic_partition])
            else:
                log.debug('Missing key %s in anomaly records poll dict, probably no messages arrived', anomaly_topic)
                num_anomaly_updates = 0
                anomaly_updates = []

            log.info("Got %d sensor updates and %d anomaly updates this loop", num_sensor_updates, num_anomaly_updates)

            if num_sensor_updates + num_anomaly_updates > 0:
                updates = itertools.chain(sensor_updates, anomaly_updates)
                # map the kafka messages into their equivalent parsed format
                bound_parse_fn = functools.partial(parse_kafka_message, wsctl_dict)
                updates = map(bound_parse_fn, updates)

                if log.isEnabledFor(logging.DEBUG):
                    updates = list(updates)
                    log.debug("Post parsing:")
                    for message in updates:
                        log.debug(message)

                # filter out the messages we don't want to send over the websocket
                updates = filter(lambda x: x is not None, updates)

                if log.isEnabledFor(logging.DEBUG):
                    log.debug("Post filter:")
                    updates = list(updates)
                    for message in updates:
                        log.debug(message)
                
                updates = map(lambda m: m[1], updates)
                messages = {"updates": list(updates)}

                if log.isEnabledFor(logging.DEBUG):
                    log.debug("Sending these messages over websocket:")
                    for message in messages['updates']:
                        log.debug(message)

                log.info("emitting %d updates", len(messages['updates']))

                # send the remaining messages over the websocket connection
                try:
                    await ws.send(json.dumps(messages))
                except websockets.exceptions.ConnectionClosed:
                    log.info("Websocket is closing")
                    running = False

        log.info("exiting websocket handler, websocket is closed")

    # set up the ws server
    start_server = websockets.serve(emit_loop, host, port)

    # run it and then loop forever
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
