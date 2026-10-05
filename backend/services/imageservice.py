import os
import uuid
import cv2
from werkzeug.utils import secure_filename
from backend.config import UPLOAD_FOLDER, RESULTS_FOLDER
from backend.services.evidenceservice import register_evidence

ALLOWED_EXT = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def save_upload(file):
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXT:
        raise ValueError(f"Unsupported type: {ext}")
    name = secure_filename(f"{uuid.uuid4().hex}{ext}")
    path = os.path.join(UPLOAD_FOLDER, name)
    file.save(path)
    evidence = register_evidence(path)
    return path, evidence


def save_result(image, prefix="result"):
    name = f"{prefix}_{uuid.uuid4().hex}.jpg"
    path = os.path.join(RESULTS_FOLDER, name)
    cv2.imwrite(path, image)
    return path