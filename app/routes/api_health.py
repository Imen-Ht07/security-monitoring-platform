# app/routes/api_health.py
from flask import Blueprint, jsonify
from datetime import datetime

bp_health = Blueprint("api_health", __name__, url_prefix="/api/health")


@bp_health.route("", methods=["GET"])
def health_check():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }), 200
