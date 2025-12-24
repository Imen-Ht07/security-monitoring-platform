# app/routes/api_upload.py
from flask import Blueprint, request, jsonify
from app.services.elasticsearch_service import ElasticsearchService
import csv
import json
import io
import logging

logger = logging.getLogger(__name__)

upload_bp = Blueprint("api_upload", __name__, url_prefix="/api/upload")

# Instance Elasticsearch
es_service = ElasticsearchService()


@upload_bp.route("", methods=["POST"])
def upload():
    """
    Upload log files via multipart/form-data
    """
    if "files" not in request.files:
        return jsonify({"error": "No files provided"}), 400

    files = request.files.getlist("files")
    total_records = 0
    errors = []

    try:
        es = es_service.client

        for file in files:
            try:
                # ---------- CSV ----------
                if file.filename.endswith(".csv"):
                    stream = io.StringIO(file.read().decode("utf-8"))
                    reader = csv.DictReader(stream)

                    for row in reader:
                        clean_row = {k: v for k, v in row.items() if k and v}
                        es.index(index="logs_index", document=clean_row)
                        total_records += 1

                # ---------- JSON ----------
                elif file.filename.endswith(".json"):
                    content = file.read().decode("utf-8")

                    try:
                        data = json.loads(content)

                        # JSON array
                        if isinstance(data, list):
                            for record in data:
                                es.index(index="logs_index", document=record)
                                total_records += 1
                        else:
                            es.index(index="logs_index", document=data)
                            total_records += 1

                    except json.JSONDecodeError:
                        # JSONL
                        for line in content.splitlines():
                            if line.strip():
                                record = json.loads(line)
                                es.index(index="logs_index", document=record)
                                total_records += 1

                else:
                    errors.append(f"Unsupported file type: {file.filename}")

            except Exception as e:
                error_msg = f"Error processing {file.filename}: {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)

        return jsonify({
            "success": True,
            "files_processed": len(files),
            "records_indexed": total_records,
            "errors": errors or None
        }), 201

    except Exception as e:
        logger.exception("❌ Upload failed")
        return jsonify({"error": str(e)}), 500
