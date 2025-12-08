from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from services.elasticsearch_service import ElasticsearchService
from models.uploaded_file import UploadedFile
from models.search_history import SearchHistory
import os
import csv
import json
from datetime import datetime

UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "/uploads")
ALLOWED_EXTENSIONS = {"csv", "json", "txt"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def create_app():
    app = Flask(__name__)
    app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
    app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024

    es_service = ElasticsearchService()
    uploaded_file_model = UploadedFile()
    search_history_model = SearchHistory()

    @app.route("/")
    def index():
        return """
        <h1>Security Logs Monitoring Platform</h1>
        <p>API endpoints:</p>
        <ul>
            <li>GET /api/stats - Global statistics</li>
            <li>POST /api/upload - Upload a log file</li>
            <li>GET /api/files - List uploaded files</li>
            <li>GET /api/search - Search logs</li>
            <li>POST /api/ingest - Ingest logs from files</li>
        </ul>
        """

    @app.route("/api/stats", methods=["GET"])
    def get_stats():
        """Récupère les statistiques globales"""
        stats = es_service.get_stats()
        return jsonify(stats)

    @app.route("/api/upload", methods=["POST"])
    def upload_file():
        """Upload un fichier de logs"""
        if "file" not in request.files:
            return jsonify({"error": "No file part"}), 400

        file = request.files["file"]
        source_system = request.form.get("source_system", "unknown")

        if file.filename == "":
            return jsonify({"error": "No selected file"}), 400

        if not allowed_file(file.filename):
            return jsonify({"error": "File type not allowed"}), 400

        try:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(filepath)

            with open(filepath, "r") as f:
                num_logs = sum(1 for _ in f) - 1

            file_id = uploaded_file_model.create(
                filename=filename,
                file_type=filename.rsplit(".", 1)[1].lower(),
                num_logs=num_logs,
                source_system=source_system
            )

            return jsonify({
                "message": "File uploaded successfully",
                "file_id": file_id,
                "filename": filename,
                "num_logs": num_logs,
                "status": "processing"
            }), 201

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/files", methods=["GET"])
    def get_files():
        """Récupère la liste des fichiers uploadés"""
        try:
            files = uploaded_file_model.get_all()
            return jsonify({"files": files}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/search", methods=["GET"])
    def search_logs():
        """Recherche les logs"""
        search_term = request.args.get("q", "")
        log_level = request.args.getlist("level")
        event_type = request.args.getlist("event_type")
        page = int(request.args.get("page", 0))

        date_start = request.args.get("date_start")
        date_end = request.args.get("date_end")

        filters = {}
        if log_level:
            filters["log_level"] = log_level
        if event_type:
            filters["event_type"] = event_type
        if date_start and date_end:
            filters["date_range"] = {
                "start": date_start,
                "end": date_end
            }

        try:
            result = es_service.search_logs(
                query_term=search_term,
                filters=filters,
                page=page,
                page_size=50
            )

            if result.get("logs"):
                search_history_model.create(
                    search_term=search_term,
                    filters=filters,
                    num_results=result["total"]
                )

            return jsonify(result), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/search-history", methods=["GET"])
    def get_search_history():
        """Récupère l'historique des recherches"""
        try:
            history = search_history_model.get_recent(limit=10)
            return jsonify({"history": history}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/ingest", methods=["POST"])
    def ingest_logs():
        """Ingère les logs des fichiers CSV/JSON directement"""
        try:
            logs = []
            
            # Traiter les CSV
            for csv_file in os.listdir("/uploads"):
                if csv_file.endswith(".csv"):
                    with open(f"/uploads/{csv_file}", "r") as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            log = {
                                "timestamp": row.get("timestamp"),
                                "event_type": row.get("event_type"),
                                "username": row.get("username"),
                                "source_ip": row.get("source_ip"),
                                "auth_result": row.get("auth_result"),
                                "resource_accessed": row.get("resource_accessed"),
                                "country": row.get("country"),
                                "severity": row.get("severity"),
                                "source_system": "csv_upload",
                                "@timestamp": row.get("timestamp")
                            }
                            logs.append(log)
            
            # Traiter les JSON
            for json_file in os.listdir("/uploads"):
                if json_file.endswith(".json"):
                    with open(f"/uploads/{json_file}", "r") as f:
                        for line in f:
                            try:
                                log = json.loads(line)
                                log["source_system"] = "json_upload"
                                log["@timestamp"] = log.get("timestamp")
                                logs.append(log)
                            except:
                                pass
            
            # Indexer dans Elasticsearch
            result = es_service.bulk_index_logs(logs)
            
            return jsonify({
                "message": "Logs ingested successfully",
                "indexed": result.get("indexed", 0),
                "failed": result.get("failed", 0),
                "total": len(logs)
            }), 201
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
