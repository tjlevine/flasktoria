import time
import random
import logging

from controllers.default_controller import DATA

log = logging.getLogger("websocket")
log.addHandler(logging.StreamHandler())
log.setLevel(logging.DEBUG)

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

def emit_and_sleep(socketio):
    updates = []
    if should_emit_anomaly():
        logging.debug("Emitting anomaly message")
        updates.append(gen_anomaly())
    
    if should_emit_position():
        logging.debug("Emitting position message")
        updates.append(gen_position())
    
    if should_emit_sensor_data():
        logging.debug("Emitting sensor data message")
        updates.append(gen_sensor_data())

    if should_emit_sensor_status():
        logging.debug("Emitting sensor status message")
        updates.append(gen_sensor_status())
    
    if len(updates) > 0:
        socketio.emit("message", {"updates": updates})

    socketio.sleep(1)

def emit_loop(socketio):
    while True:
        emit_and_sleep(socketio)