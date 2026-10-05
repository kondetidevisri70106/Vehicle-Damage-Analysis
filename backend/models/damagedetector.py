import os
import numpy as np
import cv2
from backend.config import (
    DETECTION_MODEL_PATH, CONF_THRESHOLD, IOU_THRESHOLD,
    DAMAGE_CLASSES, IMG_SIZE,
)

try:
    from ultralytics import YOLO
    _YOLO_AVAILABLE = True
except Exception:
    _YOLO_AVAILABLE = False


class DamageDetector:
    def __init__(self, model_path=DETECTION_MODEL_PATH):
        self.model = None
        if _YOLO_AVAILABLE and os.path.exists(model_path):
            try:
                self.model = YOLO(model_path)
                print(f"[detector] YOLO loaded from {model_path}")
            except Exception as e:
                print(f"[detector] failed to load YOLO: {e}")

    def _fallback_detect(self, img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(gray, 60, 180)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        dets = []
        h, w = img.shape[:2]
        for c in contours:
            area = cv2.contourArea(c)
            if area < 0.005 * h * w:
                continue
            x, y, bw, bh = cv2.boundingRect(c)
            dets.append({
                "class": "scratch",
                "confidence": 0.45,
                "bbox": [int(x), int(y), int(x + bw), int(y + bh)],
                "area": int(area),
            })
        return sorted(dets, key=lambda d: d["area"], reverse=True)[:5]

    def detect(self, image_path):
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Cannot read: {image_path}")

        if self.model is None:
            dets = self._fallback_detect(img)
            return dets, self._annotate(img, dets)

        results = self.model.predict(img, imgsz=IMG_SIZE, conf=CONF_THRESHOLD,
                                     iou=IOU_THRESHOLD, verbose=False)[0]
        dets = []
        for box in results.boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            dets.append({
                "class": DAMAGE_CLASSES[cls_id] if cls_id < len(DAMAGE_CLASSES) else "damage",
                "confidence": round(conf, 3),
                "bbox": [x1, y1, x2, y2],
                "area": int((x2 - x1) * (y2 - y1)),
            })
        return dets, self._annotate(img, dets)

    @staticmethod
    def _annotate(img, dets):
        out = img.copy()
        for d in dets:
            x1, y1, x2, y2 = d["bbox"]
            cv2.rectangle(out, (x1, y1), (x2, y2), (0, 0, 255), 2)
            label = f"{d['class']} {d['confidence']:.2f}"
            cv2.putText(out, label, (x1, max(y1 - 8, 15)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        return out