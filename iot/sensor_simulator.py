"""Simulate accelerometer/gyro/GPS readings and POST to backend."""
import time
import random
import requests

URL = "http://localhost:5000/api/sensor/ingest"

def run(interval=0.5):
    while True:
        payload = {
            "accel": {
                "x": random.uniform(-2, 2),
                "y": random.uniform(-2, 2),
                "z": random.uniform(9, 10),
            },
            "gyro": {
                "x": random.uniform(-1, 1),
                "y": random.uniform(-1, 1),
                "z": random.uniform(-1, 1),
            },
            "gps": {"lat": 12.9716, "lon": 77.5946},
        }
        try:
            r = requests.post(URL, json=payload, timeout=2)
            print(r.status_code, r.json())
        except Exception as e:
            print("send failed:", e)
        time.sleep(interval)
def simulate_obd():
    return {
        "type": "obd",
        "rpm": round(random.uniform(600, 3000), 0),
        "speed_kph": round(random.uniform(0, 120), 1),
        "coolant_temp_c": round(random.uniform(80, 105), 1),
        "error_codes": random.choice([[], ["P0300"], ["P0420"]]),
    }
if __name__ == "__main__":
    run()