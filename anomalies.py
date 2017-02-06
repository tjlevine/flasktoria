import logging

log = logging.getLogger("flasktoria.anomalies")
log.setLevel(logging.DEBUG)

def load_anomalies():
    from json import load
    with open('anomaly-map.json') as f:
        return load(f)

ANOMALIES = load_anomalies()

def get_anomaly_template(anomaly_id):
    if anomaly_id >= len(ANOMALIES) or anomaly_id < 0:
        log.warn("Got out of range anomaly id {}".format(anomaly_id))
        return
    
    return ANOMALIES[anomaly_id]

def create_from_template(anomaly_id, vehicle_id, detection_ts, declared_ts):
    template = get_anomaly_template(anomaly_id)

    if template is None:
        log.error('Cannot create anomaly from template! Anomaly id {} is likely invalid'.format(anomaly_id))
        return
    
    template['vehicle_id'] = vehicle_id
    template['detection_timestamp'] = detection_ts
    template['declared_timestamp'] = declared_ts

    return template

    