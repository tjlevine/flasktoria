import json
import time
import logging
import test_data
import victoria_db
from cfg import cfg

log = logging.getLogger("flasktoria.rest")
log.setLevel(logging.DEBUG)

WSCTL_DICT = None

def init_controller(kafka_msgs, wsctl_dict):
    global WSCTL_DICT
    log.info("default controller init")

    WSCTL_DICT = wsctl_dict

def map_get() -> str:
    vehicle_ids = victoria_db.get_all_vehicle_uuids()

    return {
        "vehicles": [
            {
                "name": test_data.driver_name(vid),
                "id": vid,
                "lat": val['lat'],
                "long": val['long'],
                "status": "ok"
            }
            for vid, val in victoria_db.get_map_data_for_vehicles(vehicle_ids).items()
        ],
        "updateWebSocket": cfg("WS_URL")
    }

def cost_vehicle_id_get(vehicle_id) -> str:
    ret = test_data.cost(vehicle_id)

    if ret is not None:
        return ret
    else:
        return {}, 400

def vehicle_vehicle_id_get(vehicle_id) -> str:
    vehicle = test_data.vehicle(vehicle_id)
    curtime = int(round(time.time() * 1000))
    recent_data = victoria_db.get_recent_sensor_data_for_vehicle(vehicle_id)

    if len(recent_data) == 0:
        log.debug("No recent data for vehicle {}".format(vehicle_id))
        return {
            "name": vehicle_id,
            # TODO: get actual vehicle status from database (how to determine active anomalies?)
            "status": "ok",
            "sensors": [{
                "sensor_id": sid,
                "sensor_name": sname
            } for sid, sname in test_data.sensors().items()],
            "sensordata": {
                "fuel": [],
                "speed": [],
                # no clue what KPI really means, and nobody seems to want to define this
                # just going to return an empty array
                "kpi": []
            }
        }

    log.debug("Recent items for vehicle {}: {}".format(vehicle_id, recent_data))
    fuel_data = list(filter(lambda msg: msg[0] == 'pid_47_mode_1', recent_data.items()))[0][1]
    log.debug("Fuel: {}".format(fuel_data))
    speed_data = list(filter(lambda msg: msg[0] == 'pid_13_mode_1', recent_data.items()))[0][1]
    log.debug("Speed: {}".format(speed_data))

    return {
        "name": vehicle_id,
        # TODO: get actual vehicle status from database (how to determine active anomalies?)
        "status": "ok",
        "sensors": [{
            "sensor_id": sid,
            "sensor_name": sname
        } for sid, sname in test_data.sensors().items()],
        "sensordata": {
            "fuel": fuel_data,
            "speed": speed_data,
            # no clue what KPI really means, and nobody seems to want to define this
            # just going to return an empty array
            "kpi": []
        }
    }

def anomalies_get(start_ts, end_ts = None) -> str:
    curtime = int(round(time.time() * 1000))

    if end_ts is None:
        log.debug("End timestamp is none, using curtime as end timestamp")
        end_ts = curtime

    try:
        start_ts = int(start_ts)
    except ValueError:
        log.warn("Bad start timestamp ({}), must be an integer".format(start_ts))
        return {}, 400

    try:
        end_ts = int(end_ts)
    except ValueError:
        log.warn("Bad end timestamp ({}), must be an integer".format(end_ts))
        return {}, 400

    if start_ts > curtime:
        log.warn("Start timestamp ({}) is greater than current time ({}), no data will be returned".format(start_ts, curtime))
        return {}, 400

    if start_ts >= end_ts:
        log.warn("Invalid timestamp range. Start ts ({}) is >= end ts ({})".format(start_ts, end_ts))
        return {}, 400

    if end_ts > curtime:
        log.warn("End timestamp ({}) is greater than current time ({}), using current time as end timestamp".format(end_ts, curtime))
        end_ts = curtime

    # start ts and end ts are currently ignored, this will be fixed
    return victoria_db.get_anomalies(start_ts, end_ts)

def sensordata_vehicle_id_get(vehicle_id, sensor_ids, start_ts, end_ts = None) -> str:
    log.debug("sensor data called with vehicle: {}, sensor_ids: {}, start_ts: {}, end_ts: {}".format(vehicle_id, sensor_ids, start_ts, end_ts))

    curtime = int(round(time.time() * 1000))

    sensor_ids = sensor_ids.split(',')

    if end_ts is None:
        log.debug("End timestamp is none, using curtime as end timestamp")
        end_ts = curtime

    try:
        start_ts = int(start_ts)
    except ValueError:
        log.warn("Bad start timestamp ({}), must be an integer".format(start_ts))
        return {}, 400

    try:
        end_ts = int(end_ts)
    except ValueError:
        log.warn("Bad end timestamp ({}), must be an integer".format(end_ts))
        return {}, 400
    
    if start_ts >= end_ts:
        log.warn("Invalid timestamp range. Start ts ({}) is >= end ts ({})".format(start_ts, end_ts))
        return {}, 400

    if start_ts > curtime:
        log.warn("Start timestamp ({}) is greater than current time ({}), no data will be returned".format(start_ts, curtime))
        return {}, 400
    
    if end_ts > curtime:
        log.warn("End timestamp ({}) is greater than current time ({}), using current time as end timestamp".format(end_ts, curtime))
        end_ts = curtime

    cutoff_ts = curtime - 2 * 60 * 1000

    #if start_ts < cutoff_ts and end_ts <= cutoff_ts:
        # request can be serviced entirely from the db
    sensor_data = victoria_db.get_sensor_data_for_vehicle(vehicle_id, sensor_ids, start_ts, end_ts)
    #elif start_ts < cutoff_ts and end_ts > cutoff_ts:
        # end ts is after cutoff, need to get some data from kafka cache
        #pass
    #else:
        # both start and end are after cutoff, but before curtime
        # so we must get all data from kafka cache
        #pass

    return sensor_data

def wsctl_post(wsctl) -> str:
    for wsctl_msg in wsctl:
        for field in ['action', 'update_type', 'vehicle_id', 'sensor_id']:
            if field not in wsctl_msg:
                log.warn("Required field {} missing from wsctl_msg request object {}".format(field, wsctl_msg))
                return { "success": False }, 400

        action = wsctl_msg['action']
        update_type = wsctl_msg['update_type']
        vehicle_id = wsctl_msg['vehicle_id']
        sensor_id = wsctl_msg['sensor_id']

        if action not in ['start', 'stop']:
            log.warn("Bad value for wsctl_msg action ({}), must be either 'start' or 'stop'".format(action))
            return { "success": False }, 400

        if update_type not in ['position', 'sensordata', 'sensorstatus']:
            log.warn("Bad value for wsctl_msg update type ({}), must be one of 'position', 'sensordata' or 'sensorstatus'".format(update_type))
            return { "success": False }, 400

        if not test_data.has_vehicle(vehicle_id):
            log.warn("Invalid vehicle id in wsctl_msg update ({})".format(vehicle_id))
            
            return { "success": False }, 400

        if not test_data.has_sensor(sensor_id):
            if not (update_type == 'position' and sensor_id == ''):
                log.warn("Invalid sensor id in wsctl_msg update ({})".format(sensor_id))
                return { "success": False }, 400

        if action == 'start':
            log.info('starting ws messages for update type {} on vehicle {}, sensor {}'.format(update_type, vehicle_id, sensor_id))
            key = update_type + '#' + vehicle_id + '#' + sensor_id
            if key in WSCTL_DICT:
                del WSCTL_DICT[key]
        else:
            log.info('stopping ws messages for update type {} on vehicle {}, sensor {}'.format(update_type, vehicle_id, sensor_id))
            key = update_type + '#' + vehicle_id + '#' + sensor_id
            WSCTL_DICT[update_type + '#' + vehicle_id + '#' + sensor_id] = True

    return {
        "success": True
    }
