import os
from flask import Blueprint, request, jsonify, send_file
from backend.services.imageservice import save_upload, save_result
from backend.services.multiviewservice import fuse_views
from backend.services.sensorservice import get_latest_sensor_summary
from backend.services.repairservice import recommend_repair
from backend.models.damagedetector import DamageDetector
from backend.models.severitydetector import SeverityModel
from backend.models.hiddendamagemodel import HiddenDamageModel
from backend.models.costmodel import CostModel
from backend.services.videoservice import is_video, extract_frames
from backend.services.temporalfusion import fuse_frames
from backend.services.historyservice import save_inspection
from backend.utils.calculations import severity_to_score, score_to_label

damage_bp = Blueprint("damage", __name__)
_detector = DamageDetector()
_severity = SeverityModel()
_hidden = HiddenDamageModel()
_cost = CostModel()


def _component_from_view(view, damage_class):
    mapping = {"front": "front_bumper", "rear": "rear_bumper",
               "left": "door", "right": "door", "closeup": "fender"}
    if damage_class == "broken_lamp":
        return "headlight" if view == "front" else "taillight"
    if damage_class == "shattered":
        return "windshield"
    if damage_class == "flat_tire":
        return "tire"
    return mapping.get(view, "fender")


@damage_bp.route("/analyze", methods=["POST"])
def analyze():
    view_results = {}
    annotated_paths = {}

    for view in ["front", "rear", "left", "right", "closeup"]:
        if view not in request.files:
            continue
        file = request.files[view]
        if not file or file.filename == "":
            continue
        try:
            path, evidence = save_upload(file)
            detections, annotated = _detector.detect(path)
            severity = _severity.predict(detections, annotated.shape)
            view_results[view] = {
                "detections": detections,
                "severity": severity,
                "image_path": path,
                "evidence": evidence,
            }
            annotated_paths[view] = save_result(annotated, prefix=view)
        except Exception as e:
            view_results[view] = {"error": str(e), "detections": [],
                                  "severity": {"score": 0.0, "severity": "none"}}

    if not view_results:
        return jsonify({"error": "No valid images"}), 400

    fusion = fuse_views(view_results)
    sensor = get_latest_sensor_summary()

    hidden = _hidden.predict(
        fusion["fused_severity_score"],
        sensor["impact_g"],
        sensor["rotation_dps"],
        len(fusion["fused_detections"]),
        sensor.get("obd_errors", 0),
    )

    fused_score = fusion.get("fused_severity_score", 0.0)
    sev_score = severity_to_score(fused_score)
    sev_text = "minor" if sev_score <= 30 else "moderate" if sev_score <= 60 else "severe"
    sev_label = score_to_label(sev_score)

    repair = recommend_repair(fusion["dominant_damage"], sev_text)
    component = _component_from_view(list(view_results.keys())[0],
                                     fusion["dominant_damage"])
    vehicle_type = request.form.get("vehicle_type", "car_sedan")
    cost = _cost.estimate(component, sev_text, fusion["dominant_damage"], vehicle_type)

    inspection_id = None
    try:
        inspection_id = save_inspection({
            "vehicle_type": vehicle_type,
            "dominant_damage": fusion.get("dominant_damage", "none"),
            "severity_score": sev_score,
            "severity_label": sev_label,
            "hidden_risk": hidden.get("risk_score", 0),
            "hidden_level": hidden.get("risk_level", "low"),
            "repair_action": repair.get("action", ""),
            "cost_min": cost.get("cost_min", 0),
            "cost_max": cost.get("cost_max", 0),
            "image_count": len(view_results),
            "latitude": sensor.get("location", {}).get("lat"),
            "longitude": sensor.get("location", {}).get("lon"),
        })
    except Exception as e:
        print(f"[history] save failed: {e}")

    return jsonify({
        "inspection_id": inspection_id,
        "views": view_results,
        "annotated_images": annotated_paths,
        "fusion": fusion,
        "sensor": sensor,
        "hidden_damage": hidden,
        "repair": repair,
        "cost": cost,
        "component": component,
        "vehicle_type": vehicle_type,
        "severity_score": sev_score,
        "severity_label": sev_label,
    })


@damage_bp.route("/result/<path:filename>")
def get_result(filename):
    from backend.config import RESULTS_FOLDER
    return send_file(os.path.join(RESULTS_FOLDER, filename))


@damage_bp.route("/analyze-video", methods=["POST"])
def analyze_video():
    if "video" not in request.files:
        return jsonify({"error": "No video uploaded"}), 400
    file = request.files["video"]
    if not is_video(file.filename):
        return jsonify({"error": "Unsupported video format"}), 400
    try:
        saved = save_upload(file)
        video_path = saved[0] if isinstance(saved, tuple) else saved
        frame_paths = extract_frames(video_path)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    frame_results = []
    for path in frame_paths:
        dets, annotated = _detector.detect(path)
        sev = _severity.predict(dets, annotated.shape)
        ap = save_result(annotated, prefix="video_frame")
        frame_results.append({
            "frame_path": path,
            "annotated_path": ap,
            "detections": dets,
            "severity_score": sev["score"],
        })
    return jsonify(fuse_frames(frame_results))