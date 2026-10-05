import uuid
from datetime import datetime
from backend.services.db import connect


def _make_id():
    return f"INS-{datetime.utcnow().strftime('%y%m%d%H%M%S')}-{uuid.uuid4().hex[:4].upper()}"


def save_inspection(data):
    inspection_id = data.get("inspection_id") or _make_id()
    with connect() as conn:
        conn.execute("""
            INSERT INTO inspections (
                inspection_id, created_at, vehicle_type, dominant_damage,
                severity_score, severity_label, hidden_risk, hidden_level,
                repair_action, cost_min, cost_max, image_count, user_id,
                latitude, longitude
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            inspection_id, datetime.utcnow().isoformat() + "Z",
            data.get("vehicle_type", "car_sedan"),
            data.get("dominant_damage", "none"),
            data.get("severity_score", 0),
            data.get("severity_label", ""),
            data.get("hidden_risk", 0.0),
            data.get("hidden_level", "low"),
            data.get("repair_action", ""),
            data.get("cost_min", 0),
            data.get("cost_max", 0),
            data.get("image_count", 0),
            data.get("user_id"),
            data.get("latitude"),
            data.get("longitude"),
        ))
        conn.commit()
    return inspection_id


def list_inspections(limit=50, offset=0, vehicle_type=None, severity=None):
    query = "SELECT * FROM inspections WHERE 1=1"
    params = []
    if vehicle_type:
        query += " AND vehicle_type = ?"
        params.append(vehicle_type)
    if severity:
        query += " AND severity_label = ?"
        params.append(severity)
    query += " ORDER BY id DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    with connect() as conn:
        rows = conn.execute(query, params).fetchall()
    return [dict(r) for r in rows]


def get_inspection(inspection_id):
    with connect() as conn:
        row = conn.execute(
            "SELECT * FROM inspections WHERE inspection_id = ?",
            (inspection_id,)
        ).fetchone()
    return dict(row) if row else None


def delete_inspection(inspection_id):
    with connect() as conn:
        cur = conn.execute(
            "DELETE FROM inspections WHERE inspection_id = ?",
            (inspection_id,)
        )
        conn.commit()
        return cur.rowcount > 0


def stats():
    with connect() as conn:
        total = conn.execute("SELECT COUNT(*) AS c FROM inspections").fetchone()["c"]
        by_sev = conn.execute(
            "SELECT severity_label, COUNT(*) AS c FROM inspections GROUP BY severity_label"
        ).fetchall()
        avg = conn.execute(
            "SELECT AVG((cost_min + cost_max)/2.0) AS a FROM inspections"
        ).fetchone()["a"] or 0
    return {
        "total": total,
        "by_severity": {r["severity_label"] or "Unknown": r["c"] for r in by_sev},
        "avg_cost": round(avg, 0),
    }