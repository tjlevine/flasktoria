import logging
import json
import time
import impala
import impala.dbapi

import anomalies
from cfg import cfg

log = logging.getLogger('flasktoria.db')
log.setLevel(logging.INFO)

def get_cursor():
    host = cfg('DB_HOST')
    port = cfg('DB_PORT')
    conn = impala.dbapi.connect(host=host, port=port)
    return conn.cursor()

def run_query(query, cursor):
    log.info("Running query: {}".format(query))
    curtime = int(time.time() * 1000)
    result = cursor.execute(query)
    query_time = int(time.time() * 1000) - curtime
    log.info("Query took {} ms".format(query_time))
    return result

def get_all_vehicle_uuids():
    vehicle_uuids = []
    cursor = get_cursor()
    curtime = int(time.time() * 1000)
    # all vehicles must send a data point at least every 5 mins
    cutoff = curtime - 5 * 60 * 1000
    query = 'SELECT DISTINCT uuid FROM sensor ' \
            'WHERE `timestamp` BETWEEN \'{}\' AND \'{}\''.format(cutoff, curtime)
    run_query(query, cursor)
    for row in cursor:
        vehicle_uuid, = row
        vehicle_uuids.append(vehicle_uuid)
    return vehicle_uuids

def get_map_data():
    ret = {}
    cursor = get_cursor()
    curtime = int(time.time() * 1000)
    # all vehicles must send a position update at least every 5 mins
    cutoff = curtime - 5 * 60 * 1000
    query = 'SELECT `timestamp`, sensor, uuid, value ' \
            'FROM sensor WHERE sensor=\'gps_coordinates\' AND ' \
            '`timestamp` BETWEEN \'{}\' AND \'{}\' ' \
            'ORDER BY `timestamp` DESC LIMIT 30'.format(cutoff, curtime)
    run_query(query, cursor)
    for row in cursor:
        ts, sensor, vehicle_id, value = row
        if vehicle_id in ret.keys():
            continue
        value = value.split(': ')[1].replace('[', '').replace(']', '')
        lat, longitude = value.split(',')
        ret[vehicle_id] = {'lat': lat, 'long': longitude}
    return ret

def get_sensors_for_vehicle(vehicle_id):
    sensors = []
    cursor = get_cursor()
    curtime = int(time.time() * 1000)
    # all vehicle sensors must send an update at least every 5 mins
    cutoff = curtime - 5 * 60 * 1000
    query = 'SELECT DISTINCT sensor ' \
            'FROM sensor WHERE uuid=\'{}\' AND ' \
            '`timestamp` BETWEEN \'{}\' and \'{}\' ' \
            'LIMIT 100'.format(vehicle_id, cutoff, curtime)
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
            'FROM sensor ' \
            'WHERE (uuid=\'{}\' AND sensor IN ({}) AND (`timestamp` BETWEEN \'{}\' AND \'{}\')) ' \
            'ORDER BY `timestamp` DESC'
    query = query.format(vehicle_id, array_to_query_string(sensor_ids), start_ts, end_ts)
    run_query(query, cursor)
    ret = {}
    for val, sensor, ts in cursor.fetchall():
        if sensor not in ret:
            ret[sensor] = []
        try:
            ret[sensor].append({
                'value': val.split(': ')[1],
                'timestamp': ts
            })
        except IndexError:
            log.warn("Failed to split value ({}) for sensor {}".format(val, sensor))
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

    ret = []

    for ts, detection_ts, confirm_ts, sensor_list, uuid, anomaly_id in cursor:
        log.debug("Anomaly row: ts=%s dts=%s cts=%s uuid=%s anomaly_id=%s", ts, detection_ts, confirm_ts, uuid, anomaly_id)
        # build the anomaly object and add it to the return list
        anomaly = anomalies.create_from_template(anomaly_id, uuid, detection_ts, confirm_ts)
        if anomaly is not None:
            log.debug("Anomaly object: dts=%s cts=%s uuid=%s anomaly_id=%s", anomaly['detection_timestamp'], anomaly['declared_timestamp'], anomaly['vehicle_id'], anomaly['actions'])
            ret.append(anomaly)
    return ret
