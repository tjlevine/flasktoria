
# in memory vehicle database for mock purposes
VEHICLES = {
    "10000000-0000-0000-0000-000000000000":
    {
        "name": "blur",
        "id": "10000000-0000-0000-0000-000000000000",
        "lat": 13.115647,
        "long": 55.588132,
        "status": "ok"
    },
    "20000000-0000-0000-0000-000000000000":
    {
        "name": "foo",
        "id": "20000000-0000-0000-0000-000000000000",
        "lat": 13.625841,
        "long": 55.528142,
        "status": "ok"
    },
    "30000000-0000-0000-0000-000000000000":
    {
        "name": "baz",
        "id": "30000000-0000-0000-0000-000000000000",
        "lat": 13.285273,
        "long": 55.148642,
        "status": "ok"
    },
    "40000000-0000-0000-0000-000000000000":
    {
        "name": "vroom",
        "id": "40000000-0000-0000-0000-000000000000",
        "lat": 13.815773,
        "long": 55.718242,
        "status": "ok"
    },
    "50000000-0000-0000-0000-000000000000":
    {
        "name": "pop",
        "id": "50000000-0000-0000-0000-000000000000",
        "lat": 13.495647,
        "long": 55.018932,
        "status": "ok"
    }
}

COSTS = {
        "10000000-0000-0000-0000-000000000000": {
            "cost_index": {
                "day": {
                    "value": 0.12,
                    "why": "This is a placeholder for daily cost justification"
                },
                "week": {
                    "value": 0.13,
                    "why": "This is a placeholder for weekly cost justification"
                },
                "month": {
                    "value": 0.14,
                    "why": "This is a placeholder for monthly cost justification"
                }
            },
            "efficiency_index": {
                "day": {
                    "value": 0.17,
                    "why": "This is a placeholder for daily efficiency justification"
                },
                "week": {
                    "value": 0.18,
                    "why": "This is a placeholder for weekly efficiency justification"
                },
                "month": {
                    "value": 0.19,
                    "why": "This is a placeholder for monthly efficiency justification"
                }
            }
        },
        "20000000-0000-0000-0000-000000000000": {
            "cost_index": {
                "day": {
                    "value": 0.22,
                    "why": "This is a placeholder for daily cost justification"
                },
                "week": {
                    "value": 0.23,
                    "why": "This is a placeholder for weekly cost justification"
                },
                "month": {
                    "value": 0.24,
                    "why": "This is a placeholder for monthly cost justification"
                }
            },
            "efficiency_index": {
                "day": {
                    "value": 0.27,
                    "why": "This is a placeholder for daily efficiency justification"
                },
                "week": {
                    "value": 0.28,
                    "why": "This is a placeholder for weekly efficiency justification"
                },
                "month": {
                    "value": 0.29,
                    "why": "This is a placeholder for monthly efficiency justification"
                }
            }
        },
        "30000000-0000-0000-0000-000000000000": {
            "cost_index": {
                "day": {
                    "value": 0.32,
                    "why": "This is a placeholder for daily cost justification"
                },
                "week": {
                    "value": 0.33,
                    "why": "This is a placeholder for weekly cost justification"
                },
                "month": {
                    "value": 0.34,
                    "why": "This is a placeholder for monthly cost justification"
                }
            },
            "efficiency_index": {
                "day": {
                    "value": 0.37,
                    "why": "This is a placeholder for daily efficiency justification"
                },
                "week": {
                    "value": 0.38,
                    "why": "This is a placeholder for weekly efficiency justification"
                },
                "month": {
                    "value": 0.39,
                    "why": "This is a placeholder for monthly efficiency justification"
                }
            }
        },
        "40000000-0000-0000-0000-000000000000": {
            "cost_index": {
                "day": {
                    "value": 0.42,
                    "why": "This is a placeholder for daily cost justification"
                },
                "week": {
                    "value": 0.43,
                    "why": "This is a placeholder for weekly cost justification"
                },
                "month": {
                    "value": 0.44,
                    "why": "This is a placeholder for monthly cost justification"
                }
            },
            "efficiency_index": {
                "day": {
                    "value": 0.47,
                    "why": "This is a placeholder for daily efficiency justification"
                },
                "week": {
                    "value": 0.48,
                    "why": "This is a placeholder for weekly efficiency justification"
                },
                "month": {
                    "value": 0.49,
                    "why": "This is a placeholder for monthly efficiency justification"
                }
            }
        },
        "50000000-0000-0000-0000-000000000000": {
            "cost_index": {
                "day": {
                    "value": 0.52,
                    "why": "This is a placeholder for daily cost justification"
                },
                "week": {
                    "value": 0.53,
                    "why": "This is a placeholder for weekly cost justification"
                },
                "month": {
                    "value": 0.54,
                    "why": "This is a placeholder for monthly cost justification"
                }
            },
            "efficiency_index": {
                "day": {
                    "value": 0.57,
                    "why": "This is a placeholder for daily efficiency justification"
                },
                "week": {
                    "value": 0.58,
                    "why": "This is a placeholder for weekly efficiency justification"
                },
                "month": {
                    "value": 0.59,
                    "why": "This is a placeholder for monthly efficiency justification"
                }
            }
        }
}

SENSORS = [
    {
        "sensor_id": "sensor0",
        "sensor_name": "Speed"
    },
    {
        "sensor_id": "sensor1",
        "sensor_name": "Brake Pressure"
    },
    {
        "sensor_id": "sensor2",
        "sensor_name": "Ambient Temperature"
    },
    {
        "sensor_id": "sensor3",
        "sensor_name": "Tire Pressure"
    },
    {
        "sensor_id": "sensor4",
        "sensor_name": "Engine Temperature"
    },
    {
        "sensor_id": "sensor5",
        "sensor_name": "Fuel Level"
    },
    {
        "sensor_id": "sensor6",
        "sensor_name": "Steering"
    },
    {
        "sensor_id": "sensor7",
        "sensor_name": "Throttle Position"
    }
]

SENSORDATA = {

}

ANOMALIES = [
    {
        "desc": "Electrical Malfunction",
        "cost_impact": "$15",
        "vehicle_id": "50000000-0000-0000-0000-000000000000",
        "declared_timestamp": 1484259815937,
        "detection_timestamp": 1484359815937,
        "cause": "The quantum carberator shorted the microverse battery",
        "actions": "Stopped the vehicle and called for help",
        "downtime": "1 hour"
    },
    {
        "desc": "Low Tire Pressure",
        "cost_impact": "$150",
        "vehicle_id": "20000000-0000-0000-0000-000000000000",
        "declared_timestamp": 1484209815937,
        "detection_timestamp": 1484759815937,
        "cause": "The tires fell off",
        "actions": "Called for assistance",
        "downtime": "5 hours"
    },
    {
        "desc": "High Fuel Consumption",
        "cost_impact": "$15",
        "vehicle_id": "10000000-0000-0000-0000-000000000000",
        "declared_timestamp": 1484269815937,
        "detection_timestamp": 1484389815937,
        "cause": "Spark plug malfunction in cylinder 2",
        "actions": "Scheduled vehicle for fuel system maintenance",
        "downtime": "2 hours"
    }
]

WS_URL = "/ws"

def map_get() -> str:
    return {
        "vehicles": list(VEHICLES.values()),
        "updateWebSocket": WS_URL
    }

def cost_vehicle_id_get(vehicle_id) -> str:
    return COSTS[vehicle_id]

def vehicle_vehicle_id_get(vehicle_id) -> str:
    vehicle = VEHICLES[vehicle_id]
    return {
        "name": vehicle['name'],
        "status": vehicle['status'],
        "sensors": SENSORS,
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
    return ANOMALIES


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

