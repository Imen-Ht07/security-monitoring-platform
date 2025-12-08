from pymongo import MongoClient
from datetime import datetime
import os

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://admin:changeme@mongodb:27017")

class UploadedFile:
    def __init__(self):
        self.client = MongoClient(MONGODB_URL)
        self.db = self.client["security_logs"]
        self.collection = self.db["uploaded_files"]

    def create(self, filename, file_type, num_logs, source_system=None):
        """Enregistre les métadonnées d'un fichier uploadé"""
        document = {
            "filename": filename,
            "upload_date": datetime.utcnow(),
            "file_type": file_type,
            "status": "completed",
            "num_logs_indexed": num_logs,
            "index_name": f"security-logs-{datetime.utcnow().strftime('%Y.%m.%d')}",
            "metadata": {
                "source_system": source_system or "unknown",
            }
        }
        result = self.collection.insert_one(document)
        return str(result.inserted_id)

    def get_all(self):
        """Récupère tous les fichiers uploadés"""
        files = list(self.collection.find().sort("upload_date", -1))
        for f in files:
            f["_id"] = str(f["_id"])
        return files

    def get_by_id(self, file_id):
        """Récupère un fichier par ID"""
        from bson import ObjectId
        file_doc = self.collection.find_one({"_id": ObjectId(file_id)})
        if file_doc:
            file_doc["_id"] = str(file_doc["_id"])
        return file_doc
