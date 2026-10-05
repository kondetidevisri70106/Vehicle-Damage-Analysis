import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
RESULTS_FOLDER = os.path.join(BASE_DIR, "results")
REPORTS_FOLDER = os.path.join(BASE_DIR, "reports")
DATA_FOLDER = os.path.join(BASE_DIR, "data")
ML_DIR = os.path.join(BASE_DIR, "ml")

for f in (UPLOAD_FOLDER, RESULTS_FOLDER, REPORTS_FOLDER, DATA_FOLDER):
    os.makedirs(f, exist_ok=True)

DETECTION_MODEL_PATH = os.path.join(ML_DIR, "detection", "best.pt")
SEVERITY_MODEL_PATH = os.path.join(ML_DIR, "classification", "severity_model.pkl")
HIDDEN_MODEL_PATH = os.path.join(ML_DIR, "hidden_damage", "hidden_model.pkl")
COST_MODEL_PATH = os.path.join(ML_DIR, "hidden_damage", "cost_model.pkl")

CONF_THRESHOLD = 0.35
IOU_THRESHOLD = 0.45
IMG_SIZE = 640

DAMAGE_CLASSES = [
    "scratch", "dent", "crack", "shattered",
    "broken_lamp", "flat_tire", "missing_part"
]

SEVERITY_LEVELS = ["minor", "moderate", "severe"]
RISK_LEVELS = ["low", "medium", "high", "critical"]

REPAIR_ACTIONS = {
    "scratch": "repaint",
    "dent": "repair",
    "crack": "repair",
    "shattered": "replace",
    "broken_lamp": "replace",
    "flat_tire": "replace",
    "missing_part": "replace",
}

# ---------- COMPONENT COSTS ----------
BASE_COST = {
    # Car
    "front_bumper": 6000, "rear_bumper": 5500, "hood": 9000,
    "door": 12000, "windshield": 8000, "headlight": 5000,
    "taillight": 3500, "fender": 7000, "mirror": 2500, "tire": 6000,
    # Bike
    "bike_fairing": 3500, "bike_tank": 4500, "bike_handlebar": 1800,
    "bike_exhaust": 3000, "bike_headlight": 1500, "bike_fender": 900,
    "bike_tire": 2200, "bike_seat": 1200, "bike_mirror": 600,
    # Scooter
    "scooter_body": 2800, "scooter_headlight": 1200,
    "scooter_mirror": 450, "scooter_tire": 1400,
    # Truck
    "truck_cabin": 25000, "truck_bumper": 12000, "truck_container": 45000,
    "truck_axle": 18000, "truck_tire": 8500, "truck_headlight": 4200,
    # Bus
    "bus_body": 35000, "bus_windshield": 15000, "bus_door": 22000,
    "bus_tire": 9500, "bus_mirror": 3200,
    # Auto
    "auto_body": 4500, "auto_windshield": 2200, "auto_tire": 1500,
    # Commercial
    "commercial_cabin": 28000, "commercial_chassis": 55000,
    "commercial_tire": 11000,
}

SEVERITY_MULTIPLIER = {"minor": 1.0, "moderate": 1.8, "severe": 3.0}
ACTION_MULTIPLIER = {"repaint": 1.0, "repair": 1.5, "replace": 2.5, "inspect": 0.5}

VEHICLE_TYPE_MULTIPLIER = {
    "car_hatchback": 0.9,
    "car_sedan": 1.0,
    "car_suv": 1.25,
    "car_luxury": 2.2,
    "bike": 0.35,
    "scooter": 0.28,
    "auto_rickshaw": 0.45,
    "truck": 1.9,
    "bus": 2.1,
    "commercial": 2.0,
}

LABOR_HOURS = {"repaint": 4, "repair": 6, "replace": 3, "inspect": 2}
LABOR_RATE_PER_HOUR = 800
PAINT_COST_PER_PANEL = 4500