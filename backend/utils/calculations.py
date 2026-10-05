import numpy as np


def compute_severity_score(area_ratio, num_damages, avg_confidence):
    area_score = min(area_ratio * 3.0, 1.0)
    count_score = min(num_damages / 6.0, 1.0)
    score = 0.5 * area_score + 0.3 * count_score + 0.2 * avg_confidence
    return float(np.clip(score, 0.0, 1.0))


def score_to_severity(score):
    if score < 0.35: return "minor"
    if score < 0.65: return "moderate"
    return "severe"


def compute_hidden_risk(severity_score, impact_g, rotation_dps, num_damages, obd_errors=0):
    impact_score = min(impact_g / 6.0, 1.0)
    rotation_score = min(rotation_dps / 180.0, 1.0)
    count_score = min(num_damages / 6.0, 1.0)
    obd_score = min(obd_errors / 3.0, 1.0)
    risk = (0.35 * severity_score + 0.25 * impact_score +
            0.15 * rotation_score + 0.15 * count_score + 0.10 * obd_score)
    return float(np.clip(risk, 0.0, 1.0))


def risk_to_level(risk):
    if risk < 0.35: return "low"
    if risk < 0.65: return "medium"
    if risk < 0.85: return "high"
    return "critical"


def estimate_cost(component, severity, action, vehicle_type="car_sedan"):
    from backend.config import (
        BASE_COST, SEVERITY_MULTIPLIER, ACTION_MULTIPLIER,
        VEHICLE_TYPE_MULTIPLIER, LABOR_HOURS, LABOR_RATE_PER_HOUR,
        PAINT_COST_PER_PANEL,
    )
    base = BASE_COST.get(component, 5000)
    sev_m = SEVERITY_MULTIPLIER.get(severity, 1.5)
    act_m = ACTION_MULTIPLIER.get(action, 1.5)
    veh_m = VEHICLE_TYPE_MULTIPLIER.get(vehicle_type, 1.0)

    parts = base * sev_m * act_m * veh_m
    labor = LABOR_HOURS.get(action, 4) * LABOR_RATE_PER_HOUR * veh_m
    paint = PAINT_COST_PER_PANEL * veh_m if action == "repaint" else 0
    mid = parts + labor + paint
    return int(mid * 0.85), int(mid * 1.25)


def severity_to_score(severity_score) -> int:
    try:
        value = float(severity_score)
    except (TypeError, ValueError):
        return 0
    value = max(0.0, min(1.0, value))
    return int(round(value * 100))


def score_to_label(score) -> str:
    try:
        score = float(score)
    except (TypeError, ValueError):
        return "Unknown"
    if score <= 30: return "Minor"
    if score <= 60: return "Moderate"
    if score <= 80: return "Severe"
    return "Critical"