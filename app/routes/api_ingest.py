# app/routes/api_ingest.py
from flask import Blueprint, jsonify
import os
import csv
import json
import logging
from app.services.elasticsearch_service import ElasticsearchService

logger = logging.getLogger(__name__)

bp_ingest = Blueprint("api_ingest", __name__, url_prefix="/api/ingest")

es_service = ElasticsearchService()


def find_upload_dir():
    """Cherche le dossier upload dans plusieurs emplacements"""
    possible_paths = [
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads"),
        "/uploads",
        "./uploads",
        "uploads"
    ]

    for path in possible_paths:
        if os.path.exists(path) and os.path.isdir(path):
            logger.info(f"✅ Found upload dir: {path}")
            return path

    return None


@bp_ingest.route("", methods=["POST"])
def ingest_logs():
    """POST /api/ingest - Ingère les logs CSV & JSON"""

    try:
        upload_dir = find_upload_dir()
        logs = []
        files_processed = []

        if not upload_dir:
            return jsonify({
                "message": "Upload directory not found",
                "indexed": 0,
                "failed": 0,
                "total": 0
            }), 404

        logger.info(f"📥 Starting ingestion from {upload_dir}")

        for file_name in os.listdir(upload_dir):
            path = os.path.join(upload_dir, file_name)

            # ---------- CSV ----------
            if file_name.endswith(".csv"):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        reader = csv.DictReader(f)
                        count = 0
                        for row in reader:
                            logs.append({
                                "event_type": row.get("event_type"),
                                "username": row.get("username"),
                                "source_ip": row.get("source_ip"),
                                "severity": row.get("severity", "INFO"),
                                "country": row.get("country"),
                                "auth_result": row.get("auth_result"),
                                "resource_accessed": row.get("resource_accessed"),
                                "source_system": "csv_upload",
                                "@timestamp": row.get("timestamp") or None
                            })
                            count += 1
                        files_processed.append(f"CSV: {file_name} ({count})")
                except Exception as e:
                    logger.error(f"Erreur CSV {file_name}: {str(e)}")

            # ---------- JSON ----------
            elif file_name.endswith(".json"):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        count = 0
                        for line in f:
                            if not line.strip():
                                continue
                            log = json.loads(line)
                            log["source_system"] = "json_upload"
                            log["@timestamp"] = log.get("timestamp") or None
                            logs.append(log)
                            count += 1
                        files_processed.append(f"JSON: {file_name} ({count})")
                except Exception as e:
                    logger.error(f"Erreur JSON {file_name}: {str(e)}")

        logger.info(f"📊 Total logs collected: {len(logs)}")

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
        logger.exception("❌ Erreur ingestion")
        return jsonify({"error": str(e)}), 500
