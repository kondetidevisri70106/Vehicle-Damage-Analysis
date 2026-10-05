from flask import Blueprint, request, jsonify, send_file
from backend.services.reportservice import save_json_report, generate_pdf_report

report_bp = Blueprint("report", __name__)


@report_bp.route("/generate", methods=["POST"])
def generate():
    payload = request.get_json(force=True)
    if not payload:
        return jsonify({"error": "Empty payload"}), 400
    json_path = save_json_report(payload)
    pdf_path = generate_pdf_report(payload)
    return jsonify({"json_report": json_path, "pdf_report": pdf_path})


@report_bp.route("/download", methods=["GET"])
def download():
    path = request.args.get("path")
    if not path:
        return jsonify({"error": "Missing path"}), 400
    return send_file(path, as_attachment=True)