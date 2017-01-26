import time
import random
import logging
import json
import asyncio
import queue
import multiprocessing

import test_data
from cfg import cfg

log = logging.getLogger("flasktoria.ws")

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
    
    consumer = KafkaConsumer(topic, group_id='flasktoria', bootstrap_servers=[kafka_bootstrap_server])

    for msg in consumer:
        #bytes_reader = io.BytesIO(msg.value)
        #decoder = avro.io.BinaryDecoder(bytes_reader)
        #reader = avro.io.DatumReader(avro_schema)
        #record = reader.read(decoder)
        #print("Received kafka message: {}".format(record))
        print("Received kafka message: {}".format(msg.value))
        msg_queue.put(msg)


def get_kafka_updates(msg_queue):
    updates = []
    while True:
        try:
            updates.append(msg_queue.get(block=False).value.decode('utf-8'))
        except queue.Empty:
            return updates


def ws_main(wsctl_dict):
    import os
    import websockets
    import asyncio

    log.debug('in ws main (pid is {})'.format(os.getpid()))

    # start the kafka consumer process
    mgr = multiprocessing.Manager()
    kafka_msg_queue = mgr.Queue()

    kafka_process = multiprocessing.Process(target=start_kafka_consumer, args=(kafka_msg_queue,))
    kafka_process.start()

    # read config to find host and port to set up ws server on
    _, _, port = cfg('WS_URL').split(':')
    host = "0.0.0.0"
    log.debug('starting ws server on {}:{}'.format(host, port))

    # define our emit loop as a closure so we can access wsctl_dict
    async def emit_loop(ws, path):
        while True:
            #updates = test_data.get_test_updates()
            updates = get_kafka_updates(kafka_msg_queue)
            if len(updates) > 0:
                log.debug("emitting {} updates".format(len(updates)))
                await ws.send(json.dumps({"updates": updates}))
            
            await asyncio.sleep(1)

    # set up the ws server
    start_server = websockets.serve(emit_loop, host, port)

    # run it and then loop forever
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()