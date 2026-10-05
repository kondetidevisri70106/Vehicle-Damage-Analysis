from flask import Flask, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from backend.config import UPLOAD_FOLDER

from backend.routes.damageroutes import damage_bp
from backend.routes.sensorroutes import sensor_bp
from backend.routes.reportroutes import report_bp
from backend.routes.historyroutes import history_bp
from backend.routes.shoproutes import shop_bp
from backend.routes.authroutes import auth_bp
from backend.routes.evidenceroutes import evidence_bp

socketio = SocketIO(cors_allowed_origins="*", async_mode="threading")


def create_app():
    app = Flask(__name__, static_folder="../frontend", static_url_path="")
    app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
    app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024
    CORS(app)
    socketio.init_app(app)

    app.register_blueprint(damage_bp, url_prefix="/api/damage")
    app.register_blueprint(sensor_bp, url_prefix="/api/sensor")
    app.register_blueprint(report_bp, url_prefix="/api/report")
    app.register_blueprint(history_bp, url_prefix="/api/history")
    app.register_blueprint(shop_bp, url_prefix="/api/shop")
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(evidence_bp, url_prefix="/api/evidence")

    @app.route("/")
    def index():
        return app.send_static_file("index.html")

    @app.route("/api/health")
    def health():
        return jsonify({"status": "ok"})

    return app


@socketio.on("connect")
def on_connect():
    print("[SocketIO] client connected")
    emit("server_message", {"status": "connected"})


@socketio.on("disconnect")
def on_disconnect():
    print("[SocketIO] client disconnected")


@socketio.on("sensor_stream")
def handle_sensor(data):
    from backend.services.sensorservice import ingest_sensor
    try:
        ingest_sensor(data)
    except ValueError as e:
        emit("sensor_error", {"error": str(e)})
        return
    if data.get("type") == "accelerometer" and float(data.get("magnitude", 0)) > 4.0:
        emit("impact_alert", {
            "magnitude": float(data["magnitude"]),
            "message": f"Impact detected: {data['magnitude']} G",
        }, broadcast=True)


if __name__ == "__main__":
    app = create_app()
    socketio.run(app, host="0.0.0.0", port=5000, debug=True, allow_unsafe_werkzeug=True)