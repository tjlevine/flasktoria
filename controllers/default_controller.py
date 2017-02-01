import json
import logging
import test_data
import victoria_db
from cfg import cfg

log = logging.getLogger("flasktoria.rest")

DATA = test_data.load_data()

def map_get() -> str:
    vehicle_ids = victoria_db.get_all_vehicle_uuids()

    return {
        "vehicles": {
            vid: {
                "name": vid,
                "id": vid,
                "lat": DATA["VEHICLES"][vid]["lat"],
                "long": DATA["VEHICLES"][vid]["long"],
                "status": DATA["VEHICLES"][vid]["status"]
            }
            for vid in vehicle_ids
        },
        "updateWebSocket": cfg("WS_URL")
    }

    #return {
    #    "vehicles": list(DATA["VEHICLES"].values()),
    #    "updateWebSocket": cfg("WS_URL")
    #}

def cost_vehicle_id_get(vehicle_id) -> str:
    return DATA["COSTS"][vehicle_id]

def vehicle_vehicle_id_get(vehicle_id) -> str:
    vehicle = DATA["VEHICLES"][vehicle_id]
    return {
        "name": vehicle['name'],
        "status": vehicle['status'],
        "sensors": DATA["SENSORS"],
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
    return DATA["ANOMALIES"]


def sensordata_vehicle_id_get(vehicle_id, sensor_ids, start_ts, end_ts = None) -> str:
    # arguments are currently ignored, this will be fixed
    return {
        "sensor0": [
            {
                "timestamp": 1484259815937,
                "value": 0
            }
        ],
        "sensor1": [
            {
                "timestamp": 1484259815937,
                "value": 0
            }
        ],
        "sensor2": [
            {
                "timestamp": 1484259815937,
                "value": 0
            }
        ],
        "sensor3": [
            {
                "timestamp": 1484259815937,
                "value": 0
            }
        ],
        "sensor4": [
            {
                "timestamp": 1484259815937,
                "value": 0
            }
        ],
        "sensor5": [
            {
                "timestamp": 1484259815937,
                "value": 0
            }
        ],
        "sensor6": [
            {
                "timestamp": 1484259815937,
                "value": 0
            }
        ],
        "sensor7": [
            {
                "timestamp": 1484259815937,
                "value": 0
            }
        ]
    }

def wsctl_post(wsctl) -> str:
    return {
        "success": True
    }
