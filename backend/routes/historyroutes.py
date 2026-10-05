from flask import Blueprint, jsonify, request
from backend.services.historyservice import (
    list_inspections, get_inspection, delete_inspection, stats,
)

history_bp = Blueprint("history", __name__)


@history_bp.route("/", methods=["GET"])
def list_all():
    limit = int(request.args.get("limit", 50))
    offset = int(request.args.get("offset", 0))
    vehicle_type = request.args.get("vehicle_type")
    severity = request.args.get("severity")
    return jsonify(list_inspections(limit, offset, vehicle_type, severity))


@history_bp.route("/<inspection_id>", methods=["GET"])
def get_one(inspection_id):
    row = get_inspection(inspection_id)
    if not row:
        return jsonify({"error": "not found"}), 404
    return jsonify(row)


@history_bp.route("/<inspection_id>", methods=["DELETE"])
def remove(inspection_id):
    if delete_inspection(inspection_id):
        return jsonify({"status": "deleted"})
    return jsonify({"error": "not found"}), 404


@history_bp.route("/stats", methods=["GET"])
def get_stats():
    return jsonify(stats())