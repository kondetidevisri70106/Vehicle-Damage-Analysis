import os
import joblib
import numpy as np
from backend.config import SEVERITY_MODEL_PATH
from backend.utils.calculations import compute_severity_score, score_to_severity


class SeverityModel:
    def __init__(self, path=SEVERITY_MODEL_PATH):
        self.model = None
        if os.path.exists(path):
            try:
                self.model = joblib.load(path)
                print(f"[severity] model loaded from {path}")
            except Exception as e:
                print(f"[severity] failed to load: {e}")

    def predict(self, detections, image_shape):
        h, w = image_shape[:2]
        if not detections:
            return {"severity": "none", "score": 0.0}

        total_area = sum(d["area"] for d in detections)
        area_ratio = total_area / (h * w)
        num = len(detections)
        avg_conf = float(np.mean([d["confidence"] for d in detections]))

        if self.model is not None:
            try:
                features = np.array([[area_ratio, num, avg_conf]])
                score = float(self.model.predict_proba(features)[0][-1])
            except Exception:
                score = compute_severity_score(area_ratio, num, avg_conf)
        else:
            score = compute_severity_score(area_ratio, num, avg_conf)

        return {
            "severity": score_to_severity(score),
            "score": round(score, 3),
            "area_ratio": round(area_ratio, 4),
            "num_damages": num,
        }