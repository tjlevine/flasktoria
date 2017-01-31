import impala
import impala.dbapi

def get_cursor():
    conn = impala.dbapi.connect(host="pnda-proxy", port=21050)
    return conn.cursor()

def get_all_vehicle_uuids():
    vehicle_uuids = []
    cursor = get_cursor()
    cursor.execute('SELECT DISTINCT uuid FROM depa_raw LIMIT 100')
    for row in cursor:
        vehicle_uuid, = row
        vehicle_uuids.append(vehicle_uuid)
    return vehicle_uuids

def get_latest_vehicle_positions(vehicle_ids):
    pass

def get_sensors_for_vehicle(vehicle_id):
    sensors = []
    cursor = get_cursor()
    query = 'SELECT DISTINCT sensor FROM depa_raw WHERE uuid=\'{}\' LIMIT 100'.format(vehicle_id)
    cursor.execute(query)
    for row in cursor:
        sensor, = row
        sensors.append(sensor)
    return sensors

def sensor_ids_query_string(sensor_ids):
    result = ''
    sensor_ids = list(map(lambda s: "'{}'".format(s), sensor_ids))
    for sensor in sensor_ids[:len(sensor_ids) - 1]:
        result += sensor + ', '
    result += sensor_ids[len(sensor_ids) - 1]
    return result


def get_sensor_data_for_vehicle(vehicle_id, sensor_ids, start_ts, end_ts):
    sensor_data = []
    # create the sensor id string which will go in the query
    cursor = get_cursor()
    query = 'SELECT value, sensor, `timestamp` ' \
            'FROM depa_raw ' \
            'WHERE (uuid=\'{}\' AND sensor IN ({}) AND (`timestamp` BETWEEN {} AND {}))'
    query = query.format(vehicle_id, sensor_ids_query_string(sensor_ids), start_ts, end_ts)
    cursor.execute(query)
    return list(cursor)
