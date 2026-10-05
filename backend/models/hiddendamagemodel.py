import os
import joblib
import numpy as np
from backend.config import HIDDEN_MODEL_PATH
from backend.utils.calculations import compute_hidden_risk, risk_to_level


class HiddenDamageModel:
    def __init__(self, path=HIDDEN_MODEL_PATH):
        self.model = None
        if os.path.exists(path):
            try:
                self.model = joblib.load(path)
                print(f"[hidden] model loaded from {path}")
            except Exception as e:
                print(f"[hidden] failed to load: {e}")

    def predict(self, severity_score, impact_g, rotation_dps, num_damages, obd_errors=0):
        if self.model is not None:
            try:
                features = np.array([[severity_score, impact_g,
                                      rotation_dps, num_damages]])
                risk = float(self.model.predict_proba(features)[0][1])
            except Exception:
                risk = compute_hidden_risk(severity_score, impact_g,
                                           rotation_dps, num_damages, obd_errors)
        else:
            risk = compute_hidden_risk(severity_score, impact_g,
                                       rotation_dps, num_damages, obd_errors)

        level = risk_to_level(risk)
        rec = ("Professional inspection strongly recommended."
               if level in ("high", "critical") else
               "Consider a professional inspection."
               if level == "medium" else
               "No immediate hidden damage concern.")

        return {
            "risk_score": round(risk, 3),
            "risk_level": level,
            "inspection_recommendation": rec,
        }