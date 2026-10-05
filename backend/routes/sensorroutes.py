from flask import Blueprint, request, jsonify
from backend.services.sensorservice import (
    ingest_sensor, get_latest_sensor_summary, reset_sensors,
)

sensor_bp = Blueprint("sensor", __name__)


@sensor_bp.route("/ingest", methods=["POST"])
def ingest():
    data = request.get_json(force=True)
    if not data or "type" not in data:
        return jsonify({"error": "Missing 'type'"}), 400
    try:
        return jsonify(ingest_sensor(data))
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@sensor_bp.route("/summary", methods=["GET"])
def summary():
    return jsonify(get_latest_sensor_summary())


@sensor_bp.route("/reset", methods=["POST"])
def reset():
    reset_sensors()
    return jsonify({"status": "reset"})