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
log.setLevel(logging.DEBUG)

def start_kafka_consumer(msg_queue):
    from kafka import KafkaConsumer
    import avro
    import avro.schema
    import avro.io
    import io

    topic = cfg("KAFKA_TOPIC")
    avro_path = cfg("AVRO_SCHEMA_PATH")
    kafka_bootstrap_server = cfg("KAFKA_BOOTSTRAP_SERVER")

    with open(avro_path) as fin:
        avro_schema = avro.schema.Parse(fin.read())

    log.debug("kafka bootstrap server: {}".format(kafka_bootstrap_server))
    consumer = KafkaConsumer(topic, group_id='test1', bootstrap_servers=[kafka_bootstrap_server])#, auto_offset_reset='earliest', enable_auto_commit=False)

    for msg in consumer:
        try:
            bytes_reader = io.BytesIO(msg.value)
            decoder = avro.io.BinaryDecoder(bytes_reader)
            reader = avro.io.DatumReader(avro_schema)
            record = reader.read(decoder)
            #log.debug("Received kafka message: {}".format(record))
            msg_queue.put(record)
        except AssertionError:
            log.warn("Got assertion error from avro decode on message: {}".format(msg))

def start_anomaly_kafka_consumer(msg_queue):
    from kafka import KafkaConsumer
    import avro
    import avro.schema
    import avro.io
    import io

    topic = cfg("KAFKA_ANOMALY_TOPIC")
    avro_path = cfg("AVRO_ANOMALY_SCHEMA_PATH")
    kafka_bootstrap_server = cfg("KAFKA_BOOTSTRAP_SERVER")

    with open(avro_path) as fin:
        avro_schema = avro.schema.Parse(fin.read())

    log.debug("kafka bootstrap server: {}".format(kafka_bootstrap_server))
    consumer = KafkaConsumer(topic, group_id='test1', bootstrap_servers=[kafka_bootstrap_server])#, auto_offset_reset='earliest', enable_auto_commit=False)

    for msg in consumer:
        try:
            bytes_reader = io.BytesIO(msg.value)
            decoder = avro.io.BinaryDecoder(bytes_reader)
            reader = avro.io.DatumReader(avro_schema)
            record = reader.read(decoder)
            log.debug("Received anomaly message: {}".format(record))
            msg_queue.put(record)
        except AssertionError:
            log.warn("Got assertion error from avro decode on message: {}".format(msg))

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
    anomaly = anomalies.create_from_template(msg['anomaly_id'], msg['uuid'], msg['confirmation_time'], msg['detection_time'])

    if anomaly is not None:
        anomaly['update_type'] = 'anomaly'
        return anomaly
    else:
        log.warn("Could not find anomaly template for anomaly id {}".format(anomaly_id))

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

    log.warn("Got unparseable kafka message: {}".format(msg))

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

def send_to_rest_process(updates, kafka_rest_msgs):
    # first, go through the existing list to remove expired entries
    curtime = int(round(time.time() * 1000))

    #for msg in updates:
        #log.debug("update msg: {}".format(msg))

    #for msg in kafka_rest_msgs:
        #log.debug("msg in cache: {}".format(msg))

    # filter out messages that are older than 3 minutes
    stale_msgs = filter(lambda msg: (curtime - msg[0]) >= (1000 * 60 * 3), kafka_rest_msgs)

    for msg in stale_msgs:
        kafka_rest_msgs.remove(msg)

    # add the new updates to the list shared with the rest process
    kafka_rest_msgs.extend(updates)

def ws_main(wsctl_dict, kafka_rest_msgs):
    import os
    import websockets
    import asyncio
    import signal
    import sys

    log.debug('in ws main (pid is {})'.format(os.getpid()))

    # start the kafka consumer process
    mgr = multiprocessing.Manager()
    kafka_msg_queue = mgr.Queue()
    kafka_anomaly_queue = mgr.Queue()

    kafka_process = multiprocessing.Process(target=start_kafka_consumer, args=(kafka_msg_queue,))
    kafka_process.start()
    log.debug("kafka process: {}".format(kafka_process))

    kafka_anomaly_process = multiprocessing.Process(target=start_anomaly_kafka_consumer, args=(kafka_anomaly_queue,))
    kafka_anomaly_process.start()
    log.debug("kafka anomaly process: {}".format(kafka_anomaly_process))

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
        sys.exit(0)

    signal.signal(signal.SIGTERM, sigterm_handler)

    # read config to find host and port to set up ws server on
    _, _, port = cfg('WS_URL').split(':')
    host = "0.0.0.0"
    log.debug('starting ws server on {}:{}'.format(host, port))

    # define our emit loop as a closure so we can access wsctl_dict
    async def emit_loop(ws, path):
        log.debug("entering event loop")
        while True:
            #updates = test_data.get_test_updates()
            updates = get_kafka_updates(kafka_msg_queue)
            updates += get_kafka_updates(kafka_anomaly_queue)

            if len(updates) > 0:
                #kafka_cache.add_entries(updates)
                log.debug("emitting {} updates".format(len(updates)))

                # map the kafka messages into their equivalent parsed format
                bound_parse_fn = functools.partial(parse_kafka_message, wsctl_dict)
                updates = list(map(bound_parse_fn, updates))

                #log.debug("Post parsing:")
                #afor message in updates:
                    #log.debug(message)

                # send all the messages to the rest server process
                send_to_rest_process(updates, kafka_rest_msgs)

                # filter out the messages we don't want to send over the websocket
                updates = filter_suppressed_messages(wsctl_dict, updates)

                #log.debug("Post filter:")
                #for message in updates:
                    #log.debug(message)
                
                updates = list(map(lambda m: m[1], updates))
                messages = {"updates": updates}

                #log.debug("Sending these messages over websocket:")
                #for message in updates:
                    #log.debug(message)

                # send the remaining messages over the websocket connection
                await ws.send(json.dumps(messages))

            await asyncio.sleep(1)

    # set up the ws server
    start_server = websockets.serve(emit_loop, host, port)

    # run it and then loop forever
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
