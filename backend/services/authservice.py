import os
import jwt
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from backend.services.db import connect

SECRET_KEY = os.environ.get("DAMAGEGENX_SECRET", "change-me-in-production")
TOKEN_EXPIRY_HOURS = 24


def create_user(username, password, email=None):
    pw_hash = generate_password_hash(password)
    with connect() as conn:
        try:
            conn.execute(
                "INSERT INTO users (username, email, password_hash, created_at) VALUES (?, ?, ?, ?)",
                (username, email, pw_hash, datetime.utcnow().isoformat()),
            )
            conn.commit()
        except Exception as e:
            return {"error": str(e)}
    return {"status": "ok", "username": username}


def authenticate(username, password):
    with connect() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()
    if not row or not check_password_hash(row["password_hash"], password):
        return None
    return dict(row)


def issue_token(user):
    payload = {
        "sub": user["id"],
        "username": user["username"],
        "role": user.get("role", "inspector"),
        "exp": datetime.utcnow() + timedelta(hours=TOKEN_EXPIRY_HOURS),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def verify_token(token):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.PyJWTError:
        return None


def user_from_request(request):
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None
    token = auth.split(" ", 1)[1].strip()
    payload = verify_token(token)
    if not payload:
        return None
    return {
        "id": payload.get("sub"),
        "username": payload.get("username"),
        "role": payload.get("role"),
    }