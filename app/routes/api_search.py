# app/routes/api_search.py
# Search endpoints
from flask import Blueprint, request, jsonify
from app.services.elasticsearch_service import ElasticsearchService
import logging

logger = logging.getLogger(__name__)

bp_search = Blueprint("api_search", __name__, url_prefix="/api/search")
es_service = ElasticsearchService()


# ================= SIMPLE SEARCH =================
@bp_search.route("", methods=["GET"])
def simple_search():
    try:
        query = request.args.get("q", "").strip()
        level = request.args.get("level", "").strip()
        page = max(0, int(request.args.get("page", 0)))

        filters = {}

        if level:
            valid_levels = ["INFO", "WARNING", "ERROR", "CRITICAL"]
            if level.upper() in valid_levels:
                filters["severity"] = [level.upper()]

        result = es_service.search(
            query_text=query,
            page=page,
            size=50
        )

        return jsonify({
            "success": True,
            "total": result["total"],
            "logs": result["logs"]
        }), 200

    except Exception as e:
        logger.error(f"Simple search error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

# ================= ADVANCED SEARCH =================
@bp_search.route("/advanced", methods=["POST"])
def advanced_search():
    try:
        filters = request.get_json() or {}

        page = max(0, int(filters.get("page", 0)))
        size = min(100, max(1, int(filters.get("size", 50))))

        result = es_service.advanced_search(
            filters=filters,
            page=page,
            size=size
        )

        return jsonify({
            "success": True,
            "total": result["total"],
            "logs": result["logs"],
            "page": page,
            "size": size
        }), 200

    except Exception as e:
        logger.error(f"Advanced search error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
