import logging
import json
import time
import impala
import impala.dbapi

import anomalies

log = logging.getLogger('flasktoria.db')
log.setLevel(logging.DEBUG)

def get_cursor():
    conn = impala.dbapi.connect(host="pnda-proxy", port=21050)
    return conn.cursor()

def run_query(query, cursor):
    log.debug("Running query: {}".format(query))
    curtime = int(time.time() * 1000)
    result = cursor.execute(query)
    query_time = int(time.time() * 1000) - curtime
    log.debug("Query took {} ms".format(query_time))
    return result

def get_all_vehicle_uuids():
    vehicle_uuids = []
    cursor = get_cursor()
    query = 'SELECT DISTINCT uuid FROM depa_raw LIMIT 100'
    run_query(query, cursor)
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
    run_query(query, cursor)
    for row in cursor:
        sensor, = row
        sensors.append(sensor)
    return sensors

def array_to_query_string(sensor_ids):
    result = ''
    sensor_ids = list(map(lambda s: "'{}'".format(s), sensor_ids))
    for sensor in sensor_ids[:len(sensor_ids) - 1]:
        result += sensor + ', '
    result += sensor_ids[len(sensor_ids) - 1]
    return result

def get_sensor_data_for_vehicle(vehicle_id, sensor_ids, start_ts, end_ts):
    # create the sensor id string which will go in the query
    cursor = get_cursor()
    query = 'SELECT value, sensor, `timestamp` ' \
            'FROM depa_raw ' \
            'WHERE (uuid=\'{}\' AND sensor IN ({}) AND (`timestamp` BETWEEN {} AND {})) '
    query = query.format(vehicle_id, array_to_query_string(sensor_ids), start_ts, end_ts)
    run_query(query, cursor)
    ret = {}
    for val_json, sensor, ts in cursor.fetchall():
        if sensor not in ret:
            ret[sensor] = []
        ret[sensor].append({
            'value': json.loads(val_json)['value'],
            'timestamp': ts
        })
    return ret

def get_recent_sensor_data_for_vehicle(vehicle_id):
    sensors = [
        "pid_47_mode_1",
        "pid_13_mode_1"
    ]
    cur_time = int(round(time.time() * 1000))
    start_time = cur_time - 60 * 1000
    data = get_sensor_data_for_vehicle(vehicle_id, sensors, start_time, cur_time)
    return data

def get_anomalies(start_ts, end_ts):
    cursor = get_cursor()
    query = 'SELECT `timestamp`, detection_time, confirmation_time, sensor, uuid, anomaly_id ' \
            'FROM anomaly ' \
            'WHERE (`timestamp` BETWEEN {} AND {}) ' \
            'ORDER BY `timestamp` DESC'
    query = query.format(start_ts, end_ts)
    run_query(query, cursor)
    data = cursor.fetchall()

    ret = []

    for ts, detection_ts, confirm_ts, sensor_list, uuid, anomaly_id in data:
        # build the anomaly object and add it to the return list
        ret.append(anomalies.create_from_template(anomaly_id, uuid, detection_ts, confirm_ts))
    return ret
