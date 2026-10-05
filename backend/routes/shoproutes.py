from flask import Blueprint, jsonify, request
from backend.services.shopservice import find_nearby_shops

shop_bp = Blueprint("shop", __name__)


@shop_bp.route("/nearby", methods=["GET"])
def nearby():
    try:
        lat = float(request.args.get("lat"))
        lon = float(request.args.get("lon"))
    except (TypeError, ValueError):
        return jsonify({"error": "lat and lon required"}), 400
    vehicle_type = request.args.get("vehicle_type", "car_sedan")
    shops = find_nearby_shops(lat, lon, vehicle_type)
    return jsonify({"count": len(shops), "shops": shops})