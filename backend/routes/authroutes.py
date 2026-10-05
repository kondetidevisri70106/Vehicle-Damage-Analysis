from flask import Blueprint, jsonify, request
from functools import wraps
from backend.services.authservice import (
    create_user, authenticate, issue_token, user_from_request,
)

auth_bp = Blueprint("auth", __name__)


def require_auth(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user = user_from_request(request)
        if not user:
            return jsonify({"error": "unauthorized"}), 401
        request.user = user
        return fn(*args, **kwargs)
    return wrapper


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(force=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    if not username or len(username) < 3:
        return jsonify({"error": "username too short"}), 400
    if len(password) < 6:
        return jsonify({"error": "password must be 6+ characters"}), 400
    result = create_user(username, password, data.get("email"))
    if "error" in result:
        return jsonify(result), 400
    return jsonify(result), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(force=True) or {}
    user = authenticate(data.get("username", ""), data.get("password", ""))
    if not user:
        return jsonify({"error": "invalid credentials"}), 401
    return jsonify({
        "token": issue_token(user),
        "username": user["username"],
        "role": user.get("role", "inspector"),
    })


@auth_bp.route("/me", methods=["GET"])
@require_auth
def me():
    return jsonify(request.user)