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