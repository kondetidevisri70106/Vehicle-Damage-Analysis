from flask import Blueprint, jsonify, request
from backend.services.evidenceservice import verify_evidence, list_evidence

evidence_bp = Blueprint("evidence", __name__)


@evidence_bp.route("/list", methods=["GET"])
def list_all():
    inspection_id = request.args.get("inspection_id")
    return jsonify(list_evidence(inspection_id))


@evidence_bp.route("/verify", methods=["POST"])
def verify():
    data = request.get_json(force=True) or {}
    eid = data.get("evidence_id")
    if not eid:
        return jsonify({"error": "evidence_id required"}), 400
    return jsonify(verify_evidence(
        eid,
        file_path=data.get("file_path"),
        expected_hash=data.get("expected_hash"),
    ))