import time
import random
import logging
import json
import asyncio
import queue
import functools
import multiprocessing

import anomalies

from cfg import cfg

log = logging.getLogger("flasktoria.ws")
log.setLevel(logging.INFO)

def start_kafka_consumer(msg_queue):
    from kafka import KafkaConsumer
    import avro
    import avro.schema
    import avro.io
    import io

    log = logging.getLogger('flasktoria.ws.sensor')
    log.setLevel(logging.INFO)

    topic = cfg("KAFKA_TOPIC")
    avro_path = cfg("AVRO_SCHEMA_PATH")
    kafka_bootstrap_server = cfg("KAFKA_BOOTSTRAP_SERVER")
    kafka_group_id = cfg("KAFKA_GROUP_ID")

    with open(avro_path) as fin:
        avro_schema = avro.schema.Parse(fin.read())

    log.debug("kafka bootstrap server: %s", kafka_bootstrap_server)
    consumer = KafkaConsumer(topic, group_id=kafka_group_id, bootstrap_servers=[kafka_bootstrap_server])#, auto_offset_reset='earliest', enable_auto_commit=False)

    for msg in consumer:
        try:
            bytes_reader = io.BytesIO(msg.value)
            decoder = avro.io.BinaryDecoder(bytes_reader)
            reader = avro.io.DatumReader(avro_schema)
            record = reader.read(decoder)
            #log.debug("Received sensor message: {}".format(record))
            msg_queue.put(record)
        except AssertionError:
            log.warn("Got assertion error from avro decode on message: %s", msg)

def start_anomaly_kafka_consumer(msg_queue):
    from kafka import KafkaConsumer
    import avro
    import avro.schema
    import avro.io
    import io

    log = logging.getLogger('flasktoria.ws.anomaly')
    log.setLevel(logging.INFO)

    topic = cfg("KAFKA_ANOMALY_TOPIC")
    avro_path = cfg("AVRO_ANOMALY_SCHEMA_PATH")
    kafka_bootstrap_server = cfg("KAFKA_BOOTSTRAP_SERVER")
    kafka_group_id = cfg("KAFKA_GROUP_ID")

    with open(avro_path) as fin:
        avro_schema = avro.schema.Parse(fin.read())

    log.debug("kafka bootstrap server: %s", kafka_bootstrap_server)
    consumer = KafkaConsumer(topic, group_id=kafka_group_id, bootstrap_servers=[kafka_bootstrap_server])#, auto_offset_reset='earliest', enable_auto_commit=False)

    for msg in consumer:
        try:
            bytes_reader = io.BytesIO(msg.value)
            decoder = avro.io.BinaryDecoder(bytes_reader)
            reader = avro.io.DatumReader(avro_schema)
            record = reader.read(decoder)
            #log.debug("Received anomaly message: {}".format(record))
            msg_queue.put(record)
        except AssertionError:
            log.warn("Got assertion error from avro decode on message: %s", msg)

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
        log.warn("Could not find anomaly template for anomaly id %s", anomaly_id)

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

def filter_suppressed_messages(wsctl_dict, updates):
    updates = list(filter(lambda x: x is not None, updates))
    return updates

def ws_main(wsctl_dict):
    import os
    import websockets
    import asyncio
    import signal
    import sys

    log.debug('in ws main (pid is %d)', os.getpid())

    # start the kafka consumer process
    mgr = multiprocessing.Manager()
    kafka_msg_queue = mgr.Queue()
    kafka_anomaly_queue = mgr.Queue()

    kafka_process = multiprocessing.Process(target=start_kafka_consumer, args=(kafka_msg_queue,))
    kafka_process.start()
    log.debug("kafka process: %s", kafka_process)

    kafka_anomaly_process = multiprocessing.Process(target=start_anomaly_kafka_consumer, args=(kafka_anomaly_queue,))
    kafka_anomaly_process.start()
    log.debug("kafka anomaly process: %s",kafka_anomaly_process)

    def sigterm_handler(signum, frame):
        log.debug("WS server is shutting down")
        kafka_process.terminate()
        log.debug("kafka process terminated")
        kafka_anomaly_process.terminate()
        log.debug("kafka anomaly process terminated")
        kafka_anomaly_process.join()
        kafka_process.join()
        log.debug("kafka processes joined")
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
        log.debug("entering event loop")
        while True:
            #updates = test_data.get_test_updates()
            updates = get_kafka_updates(kafka_msg_queue)
            sensor_updates = len(updates)
            updates += get_kafka_updates(kafka_anomaly_queue)
            anomaly_updates = len(updates) - sensor_updates
            log.info("Got %d sensor updates and %d anomaly updates this loop", sensor_updates, anomaly_updates)

            if len(updates) > 0:
                #kafka_cache.add_entries(updates)

                # map the kafka messages into their equivalent parsed format
                bound_parse_fn = functools.partial(parse_kafka_message, wsctl_dict)
                updates = list(map(bound_parse_fn, updates))

                log.debug("Post parsing:")
                for message in updates:
                    log.debug(message)

                # filter out the messages we don't want to send over the websocket
                updates = filter_suppressed_messages(wsctl_dict, updates)

                log.debug("Post filter:")
                for message in updates:
                    log.debug(message)
                
                updates = list(map(lambda m: m[1], updates))
                messages = {"updates": updates}

                log.debug("Sending these messages over websocket:")
                for message in updates:
                    log.debug(message)

                log.info("emitting %d updates", len(updates))

                # send the remaining messages over the websocket connection
                await ws.send(json.dumps(messages))

            await asyncio.sleep(1)

    # set up the ws server
    start_server = websockets.serve(emit_loop, host, port)

    # run it and then loop forever
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
