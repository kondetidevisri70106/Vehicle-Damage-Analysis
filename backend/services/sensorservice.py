import random
from datetime import datetime

_sensor_store = {"accelerometer": [], "gyroscope": [], "gps": [], "obd": []}


def ingest_sensor(data):
    stype = data.get("type")
    if stype not in _sensor_store:
        raise ValueError(f"Unknown sensor: {stype}")
    data["timestamp"] = datetime.utcnow().isoformat()
    _sensor_store[stype].append(data)
    return {"status": "ok", "stored": len(_sensor_store[stype])}


def get_gps_from_hardware():
    """Try to read GPS from a hardware module. Returns None if unavailable."""
    try:
        from iot.gps import GPS
        gps = GPS()
        fix = gps.read()
        if fix.get("lat") and fix.get("lon"):
            return {"lat": fix["lat"], "lon": fix["lon"]}
    except Exception:
        pass
    return None


def get_latest_sensor_summary():
    acc = _sensor_store["accelerometer"][-1] if _sensor_store["accelerometer"] else {}
    gyr = _sensor_store["gyroscope"][-1] if _sensor_store["gyroscope"] else {}
    gps = _sensor_store["gps"][-1] if _sensor_store["gps"] else {}
    obd = _sensor_store["obd"][-1] if _sensor_store["obd"] else {}

    impact_g = float(acc.get("magnitude", 0.0))
    rotation_dps = float(gyr.get("magnitude", 0.0))

    # Location: prefer HTTP-pushed GPS, fall back to hardware
    location = gps.get("location", {"lat": None, "lon": None})
    if not location.get("lat"):
        hw = get_gps_from_hardware()
        if hw:
            location = hw

    if impact_g == 0.0 and not acc:
        impact_g = round(random.uniform(1.0, 4.5), 2)
    if rotation_dps == 0.0 and not gyr:
        rotation_dps = round(random.uniform(5.0, 90.0), 2)

    return {
        "impact_g": impact_g,
        "rotation_dps": rotation_dps,
        "location": location,
        "obd_errors": len(obd.get("error_codes", [])),
    }


def reset_sensors():
    for k in _sensor_store:
        _sensor_store[k].clear()