import os
import cv2
import uuid
from backend.config import RESULTS_FOLDER

VIDEO_EXT = {".mp4", ".mov", ".avi", ".webm", ".mkv"}
FRAME_INTERVAL = 15
MAX_FRAMES = 12


def is_video(filename):
    return os.path.splitext(filename)[1].lower() in VIDEO_EXT


def extract_frames(video_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Cannot open video: {video_path}")
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if total <= 0:
        cap.release()
        raise ValueError("Empty video")
    step = max(FRAME_INTERVAL, total // MAX_FRAMES)
    paths = []
    idx = 0
    saved = 0
    while True:
        ok, frame = cap.read()
        if not ok: break
        if idx % step == 0 and saved < MAX_FRAMES:
            name = f"frame_{uuid.uuid4().hex}.jpg"
            path = os.path.join(RESULTS_FOLDER, name)
            cv2.imwrite(path, frame)
            paths.append(path)
            saved += 1
        idx += 1
    cap.release()
    if not paths:
        raise ValueError("No frames extracted")
    return paths