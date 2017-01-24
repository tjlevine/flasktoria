import time
import random
import logging
import json
import asyncio

log = logging.getLogger("flasktoria.ws")

def load_data():
    from json import load
    with open("data.json") as fin:
        return load(fin)

DATA = load_data()

def get_random_vehicle_id():
    return random.choice(list(DATA["VEHICLES"].keys()))

def get_random_anomaly():
    return random.choice(list(DATA["ANOMALIES"]))

def get_random_sensor(vehicle_id):
    return random.choice(DATA["SENSORS"])

# generate a random anomaly with the current timestamp as the declared timestamp
# and the detection timestamp as a random time between 2 and 60 seconds ago
def gen_anomaly():
    anomaly = get_random_anomaly()
    declared_timestamp = int(round(time.time()) * 1000)
    detection_timestamp = declared_timestamp - random.randint(2 * 1000, 60 * 1000)
    return {
        "update_type": "anomaly",
        "vehicle_id": get_random_vehicle_id(),
        "desc": anomaly["desc"],
        "cost_impact": anomaly["cost_impact"],
        "declared_timestamp": declared_timestamp,
        "detection_timestamp": detection_timestamp,
        "cause": anomaly["cause"],
        "actions": anomaly["actions"],
        "downtime": anomaly["downtime"]
    }

# generate a random position value within 0.05 degrees of the default lat/long
# this will make vehicles appear to jump around their original position
def gen_position_for_vehicle(vehicle_id):
    vehicle = DATA["VEHICLES"][vehicle_id]
    return vehicle["lat"] + random.uniform(-0.05, 0.05), \
           vehicle["long"] + random.uniform(-0.05, 0.05)

# generate a random position value for a random vehicle
def gen_position():
    vehicle = get_random_vehicle_id()
    lat, longitude = gen_position_for_vehicle(vehicle)
    return {
        "update_type": "position",
        "vehicle_id": vehicle,
        "lat": lat,
        "long": longitude
    }

# generate num_values sensor values with a random timestamp from the last second
def gen_sensor_values(vehicle_id, sensor_id, num_values):
    values = []
    for _ in range(num_values):
        value = random.random()
        timestamp = int(round(time.time()) * 1000) - random.randint(0, 1000)
        values.append({
            "timestamp": timestamp,
            "value": value
        })
    return values

# pick a random vehicle, then a random sensor on that vehicle.
# then generate between 1 and 3 new random values for that sensor
def gen_sensor_data():
    vehicle = get_random_vehicle_id()
    sensor = get_random_sensor(vehicle)
    return {
        "update_type": "sensordata",
        "vehicle_id": vehicle,
        "sensor_id": sensor["sensor_id"],
        "values": gen_sensor_values(vehicle, sensor, random.randint(1, 3))
    }

# pick a random vehicle, then a random sensor on that vehicle.
# then randomly pick either "low" or "high" as the new sensor status
def gen_sensor_status():
    vehicle = get_random_vehicle_id()
    sensor = get_random_sensor(vehicle)
    value = "low" if random.random() < 0.5 else "high"
    return {
        "update_type": "sensorstatus",
        "vehicle_id": vehicle,
        "sensor_id": sensor["sensor_id"],
        "value": value
    }

def should_emit_anomaly():
    # emit an anomaly once per minute, on average
    return random.random() <= 1/60

def should_emit_position():
    return random.random() <= 0.80

def should_emit_sensor_data():
    return random.random() <= 0.50

def should_emit_sensor_status():
    # 10 percent chance to change a random sensor status per step
    return random.random() <= 0.1

def get_updates():
    log.debug("Possibly generating websocket updates")
    updates = []
    if should_emit_anomaly():
        log.debug("Generating anomaly update")
        updates.append(gen_anomaly())
    
    if should_emit_position():
        log.debug("Generating position update")
        updates.append(gen_position())
    
    if should_emit_sensor_data():
        log.debug("Generating sensor data update")
        updates.append(gen_sensor_data())

    if should_emit_sensor_status():
        log.debug("Generating sensor status update")
        updates.append(gen_sensor_status())
    
    return updates
    
def ws_main(wsctl_dict):
    import os
    import websockets
    import asyncio

    log.debug('in ws main (pid is {})'.format(os.getpid()))

    # read config to find host and port to set up ws server on
    _, host, port = map(lambda s: s.replace('//', ''), DATA['WS_URL'].split(':'))
    log.debug('starting ws server on {}:{}'.format(host, port))

    # define our emit loop as a closure so we can access wsctl_dict
    async def emit_loop(ws, path):
        while True:
            updates = get_updates()
            if len(updates) > 0:
                log.debug("emitting {} updates".format(len(updates)))
                await ws.send(json.dumps({"updates": updates}))
            
            await asyncio.sleep(1)

    # set up the ws server
    start_server = websockets.serve(emit_loop, host, port)

    # run it and then loop forever
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()