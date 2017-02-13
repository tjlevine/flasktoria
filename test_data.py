import logging

log = logging.getLogger("flasktoria.test-data")
log.setLevel(logging.DEBUG)

def load_data():
    from json import load
    with open("data.json") as fin:
        return load(fin)

def test_data(key):
    data = load_data()
    return data[key]

def get_random_vehicle_id():
    return random.choice(list(test_data("VEHICLES").keys()))

def get_random_anomaly():
    return random.choice(list(test_data("ANOMALIES")))

def get_random_sensor(vehicle_id):
    return random.choice(test_data("SENSORS"))

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
    vehicle = test_data("VEHICLES")[vehicle_id]
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

def get_test_updates():
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

DATA = load_data()

def vehicle(vehicle_id):
    if has_vehicle(vehicle_id):
        return DATA['VEHICLES'][vehicle_id]

def has_vehicle(vehicle_id):
    if 'VEHICLES' not in DATA:
        log.warn('Vehicles key is not in test data!')
        return

    if vehicle_id in DATA['VEHICLES']:
        return True
    else:
        log.warn('Vehicle id {} is not present in vehicle test data!'.format(vehicle_id))
        return False

def cost(vehicle_id):
    costs = [
        {
            "value": "4.3% Over Budget Y2Y",
            "why": "Higher than Budgeted Fuel Costs due Inclement Weather in Spring This Year"
        },
        {
            "value": "6.7% under Budget over Last 2 Quarters",
            "why": "Reduction in Average Idle Times through Improved Tracking"
        },
        {
            "value": "3.2% Reduction in Lost Productivity This Year",
            "why": "Investment in Poor Driver Awareness and Eduction"
        }
    ]
    return random.choice(costs)

def sensors():
    return DATA['SENSORS']

def has_sensor(sensor_id):
    return sensor_id in DATA['SENSORS'].keys()

def anomalies():
    return DATA['ANOMALIES']

def driver_name(vehicle_id):
    return "DRIVER FOR {}".format(vehicle_id)
