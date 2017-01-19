import json

def load_data():
    with open("data.json") as fin:
        return json.load(fin)

DATA = load_data()

def map_get() -> str:
    return {
        "vehicles": list(DATA["VEHICLES"].values()),
        "updateWebSocket": DATA["WS_URL"]
    }

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
    print("wsctl argument:")
    print(wsctl)
    return 'Not yet implemented'

