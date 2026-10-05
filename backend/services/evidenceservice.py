"""SHA-256 hashing + audit trail for uploaded evidence."""
import os
import uuid
import hashlib
import json
from datetime import datetime
from backend.config import DATA_FOLDER
from backend.services.db import connect

LOG_PATH = os.path.join(DATA_FOLDER, "evidence_log.json")


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def register_evidence(file_path, inspection_id=None, uploader="anonymous"):
    evidence_id = f"EV-{uuid.uuid4().hex[:10].upper()}"
    file_hash = _sha256(file_path)
    entry = {
        "evidence_id": evidence_id,
        "inspection_id": inspection_id,
        "filename": os.path.basename(file_path),
        "sha256": file_hash,
        "size_bytes": os.path.getsize(file_path),
        "uploaded_at": datetime.utcnow().isoformat() + "Z",
        "uploader": uploader,
    }
    try:
        with connect() as conn:
            conn.execute("""
                INSERT INTO evidence (evidence_id, inspection_id, filename,
                    sha256, size_bytes, uploaded_at, uploader)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (entry["evidence_id"], entry["inspection_id"], entry["filename"],
                  entry["sha256"], entry["size_bytes"],
                  entry["uploaded_at"], entry["uploader"]))
            conn.commit()
    except Exception as e:
        print(f"[evidence] db insert failed: {e}")

    try:
        log = []
        if os.path.exists(LOG_PATH):
            with open(LOG_PATH) as f:
                log = json.load(f)
        log.append(entry)
        with open(LOG_PATH, "w") as f:
            json.dump(log, f, indent=2)
    except Exception as e:
        print(f"[evidence] log write failed: {e}")

    return entry


def verify_evidence(evidence_id, file_path=None, expected_hash=None):
    with connect() as conn:
        row = conn.execute(
            "SELECT * FROM evidence WHERE evidence_id = ?", (evidence_id,)
        ).fetchone()
    if not row:
        return {"valid": False, "reason": "evidence_id not found"}
    record = dict(row)
    if file_path and os.path.exists(file_path):
        current = _sha256(file_path)
        if current == record["sha256"]:
            return {"valid": True, "record": record}
        return {"valid": False, "reason": "hash mismatch",
                "record": record, "current_hash": current}
    if expected_hash:
        if expected_hash == record["sha256"]:
            return {"valid": True, "record": record}
        return {"valid": False, "reason": "hash mismatch", "record": record}
    return {"valid": True, "record": record, "note": "no file to verify"}


def list_evidence(inspection_id=None):
    with connect() as conn:
        if inspection_id:
            rows = conn.execute(
                "SELECT * FROM evidence WHERE inspection_id = ? ORDER BY id DESC",
                (inspection_id,)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM evidence ORDER BY id DESC LIMIT 100"
            ).fetchall()
    return [dict(r) for r in rows]