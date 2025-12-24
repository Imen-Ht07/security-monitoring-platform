# app/routes/api_stats.py
# Stats and aggregations endpoints
from flask import Blueprint, request, jsonify
from app.services.elasticsearch_service import ElasticsearchService
import logging

logger = logging.getLogger(__name__)

bp_stats = Blueprint("api_stats", __name__, url_prefix="/api/stats")
es_service = ElasticsearchService()


# ================= GLOBAL STATS =================
@bp_stats.route("", methods=["GET"])
def global_stats():
    try:
        return jsonify(es_service.get_stats()), 200
    except Exception as e:
        logger.error(f"Stats error: {e}")
        return jsonify({"error": str(e)}), 500


# ================= TOP IPs =================
@bp_stats.route("/top-ips", methods=["POST"])
def top_ips():
    try:
        data = request.get_json() or {}
        limit = int(data.get("limit", 10))
        result = es_service.get_top_ips(limit=limit)
        return jsonify({"success": True, "data": result}), 200
    except Exception as e:
        logger.error(f"Top IPs error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# ================= SEVERITY DISTRIBUTION =================
@bp_stats.route("/severity", methods=["GET"])
def severity_distribution():
    try:
        result = es_service.get_severity_distribution()
        return jsonify({"success": True, "data": result}), 200
    except Exception as e:
        logger.error(f"Severity error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
