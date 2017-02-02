import json
import time
import logging
import test_data
import victoria_db
from cfg import cfg

log = logging.getLogger("flasktoria.rest")

def map_get() -> str:
    vehicle_ids = victoria_db.get_all_vehicle_uuids()

    return {
        "vehicles": {
            vid: {
                "name": vid,
                "id": vid,
                "lat": test_data.vehicle(vid)["lat"],
                "long": test_data.vehicle(vid)["long"],
                "status": test_data.vehicle(vid)["status"]
            }
            for vid in vehicle_ids if test_data.has_vehicle(vid)
        },
        "updateWebSocket": cfg("WS_URL")
    }

def cost_vehicle_id_get(vehicle_id) -> str:
    ret = test_data.cost(vehicle_id)

    if ret is not None:
        return ret
    else:
        return {}, 400

def vehicle_vehicle_id_get(vehicle_id) -> str:
    if not test_data.has_vehicle(vehicle_id):
        return {}, 400

    vehicle = test_data.vehicle(vehicle_id)
    return {
        "name": vehicle_id,
        "status": vehicle['status'],
        "sensors": [{
            "sensor_id": sid,
            "sensor_name": sname
        } for sid, sname in test_data.sensors().items()],
        "sensordata": {
            "fuel": [
                {
                    "timestamp": 1484259815937,
                    "value": 0.31
                }
            ],
            "speed": [
                {
                    "timestamp": 1484259815937,
                    "value": 22.4
                }
            ],
            "kpi": [
                {
                    "timestamp": 1484259815937,
                    "value": 0
                }
            ]
        }
    }

def anomalies_get(start_ts, end_ts = None) -> str:
    # start ts and end ts are currently ignored, this will be fixed
    return test_data.anomalies()

def sensordata_vehicle_id_get(vehicle_id, sensor_ids, start_ts, end_ts = None) -> str:
    curtime = int(round(time.time() * 1000))

    sensors = test_data.sensors()

    if end_ts is None:
        log.debug("End timestamp is none, using curtime as end timestamp")
        end_ts = curtime

    if start_ts > curtime:
        log.warn("Start timestamp ({}) is greater than current time ({}), no data will be returned")
        return {}
    
    if start_ts >= end_ts:
        log.warn("Invalid timestamp range. Start ts ({}) is >= end ts ({})".format(start_ts, end_ts))
    
    if end_ts > curtime:
        log.warn("End timestamp ({}) is greater than current time ({}), using current time as end timestamp")
        end_ts = curtime

    cutoff_ts = curtime - 2 * 60 * 1000

    if start_ts < cutoff_ts and end_ts <= cutoff_ts:
        # request can be serviced entirely from the db
        sensor_data = victoria_db.get_sensor_data_for_vehicle()
    elif start_ts < cutoff_ts and end_ts > cutoff_ts:
        # end ts is after cutoff, need to get some data from kafka cache
        pass
    else:
        # both start and end are after cutoff, but before curtime
        # so we must get all data from kafka cache
        pass

    ret = {
        sensor_id: [
            
        ]
        for sensor_id in sensors.keys()
    }

    return ret
        
    # arguments are currently ignored, this will be fixed
    #return {
    #    "sensor0": [
    #        {
    #            "timestamp": 1484259815937,
    #            "value": 0
    #        }
    #    ],
    #    "sensor1": [
    #        {
    #            "timestamp": 1484259815937,
    #            "value": 0
    #        }
    #    ],
    #    "sensor2": [
    #        {
    #            "timestamp": 1484259815937,
    #            "value": 0
    #        }
    #    ],
    #    "sensor3": [
    #        {
    #            "timestamp": 1484259815937,
    #            "value": 0
    #        }
    #    ],
    #    "sensor4": [
    #        {
    #            "timestamp": 1484259815937,
    #            "value": 0
    #        }
    #    ],
    #    "sensor5": [
    #        {
    #            "timestamp": 1484259815937,
    #            "value": 0
    #        }
    #    ],
    #    "sensor6": [
    #        {
    #            "timestamp": 1484259815937,
    #            "value": 0
    #        }
    #    ],
    #    "sensor7": [
    #        {
    #            "timestamp": 1484259815937,
    #            "value": 0
    #        }
    #    ]
    #}

def wsctl_post(wsctl) -> str:
    return {
        "success": True
    }
