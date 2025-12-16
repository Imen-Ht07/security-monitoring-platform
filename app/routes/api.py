from flask import Blueprint, request, jsonify
import os
import csv
import json
from datetime import datetime
import logging

from services.elasticsearch_service import ElasticsearchService
from models.uploaded_file import UploadedFile
from models.search_history import SearchHistory

logger = logging.getLogger(__name__)

bp = Blueprint("api", __name__, url_prefix="/api")

es_service = ElasticsearchService()
uploaded_file_model = UploadedFile()
search_history_model = SearchHistory()


# =========================
#          STATS
# =========================
@bp.route("/stats", methods=["GET"])
def get_stats():
    """GET /api/stats - Récupère les statistiques globales"""
    try:
        stats = es_service.get_stats()
        return jsonify(stats), 200
    except Exception as e:
        logger.error(f"Erreur stats: {str(e)}")
        return jsonify({"error": str(e)}), 500


# =========================
#          SEARCH
# =========================
@bp.route("/search", methods=["GET"])
def search_logs():
    """GET /api/search - Recherche les logs"""

    try:
        search_term = request.args.get("q", "").strip()
        log_level = request.args.get("level", "").strip()
        page = int(request.args.get("page", 0))

        if page < 0:
            page = 0

        filters = {}

        if log_level:
            valid_levels = ["INFO", "WARNING", "ERROR", "CRITICAL"]
            if log_level.upper() in valid_levels:
                filters["log_level"] = log_level.upper()
            else:
                logger.warning(f"Niveau de sévérité invalide: {log_level}")

        result = es_service.search_logs(
            query_term=search_term,
            filters=filters,
            page=page,
            page_size=50
        )

        # Enregistrer l'historique
        if result.get("logs"):
            try:
                search_history_model.create(
                    search_term=search_term,
                    filters=filters,
                    num_results=result["total"]
                )
            except Exception as e:
                logger.warning(
                    f"Erreur enregistrement historique: {str(e)}"
                )

        return jsonify(result), 200

    except ValueError:
        return jsonify({"error": "Paramètres invalides"}), 400
    except Exception as e:
        logger.error(f"Erreur recherche: {str(e)}")
        return jsonify({"error": str(e)}), 500


# =========================
#          FILES
# =========================
@bp.route("/files", methods=["GET"])
def get_files():
    """GET /api/files - Liste les fichiers uploadés"""
    try:
        files = uploaded_file_model.get_all()
        return jsonify({"files": files}), 200
    except Exception as e:
        logger.error(f"Erreur fichiers: {str(e)}")
        return jsonify({"error": str(e)}), 500


# =========================
#          INGEST
# =========================
@bp.route("/ingest", methods=["POST"])
def ingest_logs():
    """POST /api/ingest - Ingère les logs CSV & JSON"""

    try:
        upload_dir = "uploads"
        logs = []
        files_processed = []

        if not os.path.exists(upload_dir):
            return jsonify({
                "message": "Upload directory not found",
                "indexed": 0,
                "failed": 0,
                "total": 0
            }), 404

        # ---------- CSV ----------
        for file_name in os.listdir(upload_dir):
            if file_name.endswith(".csv"):
                path = os.path.join(upload_dir, file_name)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        reader = csv.DictReader(f)
                        count = 0
                        for row in reader:
                            log = {
                                "event_type": row.get("event_type"),
                                "username": row.get("username"),
                                "source_ip": row.get("source_ip"),
                                "severity": row.get("severity", "INFO"),
                                "country": row.get("country"),
                                "auth_result": row.get("auth_result"),
                                "resource_accessed": row.get("resource_accessed"),
                                "source_system": "csv_upload",
                                "@timestamp": row.get("timestamp")
                            }
                            logs.append(log)
                            count += 1

                        files_processed.append(f"CSV: {file_name} ({count})")
                except Exception as e:
                    logger.error(f"Erreur CSV {file_name}: {str(e)}")

        # ---------- JSON (JSONL) ----------
        for file_name in os.listdir(upload_dir):
            if file_name.endswith(".json"):
                path = os.path.join(upload_dir, file_name)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        count = 0
                        for line in f:
                            if not line.strip():
                                continue
                            log = json.loads(line)
                            log["source_system"] = "json_upload"
                            log["@timestamp"] = log.get("timestamp")
                            logs.append(log)
                            count += 1

                        files_processed.append(f"JSON: {file_name} ({count})")
                except Exception as e:
                    logger.error(f"Erreur JSON {file_name}: {str(e)}")

        # ---------- Indexation ----------
        if logs:
            result = es_service.bulk_index_logs(logs)
            return jsonify({
                "message": "Logs ingérés avec succès",
                "indexed": result["indexed"],
                "failed": result["failed"],
                "total": len(logs),
                "files_processed": files_processed
            }), 201

        return jsonify({
            "message": "Aucun log trouvé",
            "indexed": 0,
            "failed": 0,
            "total": 0,
            "files_processed": files_processed
        }), 200

    except Exception as e:
        logger.error(f"Erreur ingestion: {str(e)}")
        return jsonify({"error": str(e)}), 500


# =========================
#      SEARCH HISTORY
# =========================
@bp.route("/search-history", methods=["GET"])
def get_search_history():
    """GET /api/search-history - 10 dernières recherches"""
    try:
        history = search_history_model.get_recent(limit=10)
        return jsonify({"history": history}), 200
    except Exception as e:
        logger.error(f"Erreur historique: {str(e)}")
        return jsonify({"error": str(e)}), 500


# =========================
#          HEALTH
# =========================
@bp.route("/health", methods=["GET"])
def health_check():
    """GET /api/health - Health check"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }), 200
