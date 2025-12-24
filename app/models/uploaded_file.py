"""
app/models/uploaded_file.py
Modèle MongoDB pour les fichiers uploadés
"""
from datetime import datetime
from bson import ObjectId
from app.services.mongodb_service import MongoDBService
import logging

logger = logging.getLogger(__name__)

class UploadedFile:
    collection = "uploaded_files"

    def __init__(
        self,
        filename,
        original_name,
        file_type,
        file_size,
        document_count,
        indexed_count,
        description="",
        file_path="",
        id=None,
        uploaded_at=None
    ):
        self.mongo = MongoDBService()
        self.id = id or ObjectId()
        self.filename = filename
        self.original_name = original_name
        self.file_type = file_type
        self.file_size = file_size
        self.document_count = document_count
        self.indexed_count = indexed_count
        self.description = description
        self.file_path = file_path
        self.uploaded_at = uploaded_at or datetime.now()

    # ================= SAVE =================
    def save(self):
        doc = {
            "_id": self.id,
            "filename": self.filename,
            "original_name": self.original_name,
            "file_type": self.file_type,
            "file_size": self.file_size,
            "document_count": self.document_count,
            "indexed_count": self.indexed_count,
            "description": self.description,
            "file_path": self.file_path,
            "uploaded_at": self.uploaded_at,
        }
        self.mongo.insert_one(self.collection, doc)
        logger.info(f"File '{self.filename}' saved")
        return self

    # ================= GET BY ID =================
    @staticmethod
    def get_by_id(file_id):
        mongo = MongoDBService()
        try:
            doc = mongo.find_one(
                UploadedFile.collection,
                {"_id": ObjectId(file_id)}
            )
            if not doc:
                return None

            return UploadedFile(
                filename=doc["filename"],
                original_name=doc["original_name"],
                file_type=doc["file_type"],
                file_size=doc["file_size"],
                document_count=doc["document_count"],
                indexed_count=doc["indexed_count"],
                description=doc.get("description", ""),
                file_path=doc.get("file_path", ""),
                id=doc["_id"],
                uploaded_at=doc["uploaded_at"]
            )
        except Exception as e:
            logger.error(f"Get upload error: {e}")
            return None

    # ================= GET ALL =================
    @staticmethod
    def get_all():
        mongo = MongoDBService()
        docs = mongo.find_all(UploadedFile.collection)

        results = []
        for doc in sorted(docs, key=lambda x: x["uploaded_at"], reverse=True):
            results.append({
                "id": str(doc["_id"]),
                "filename": doc["filename"],
                "original_name": doc["original_name"],
                "file_type": doc["file_type"],
                "file_size": doc["file_size"],
                "document_count": doc["document_count"],
                "indexed_count": doc["indexed_count"],
                "description": doc.get("description", ""),
                "uploaded_at": doc["uploaded_at"].isoformat()
            })
        return results

    # ================= DELETE =================
    @staticmethod
    def delete_by_id(file_id):
        mongo = MongoDBService()
        result = mongo.delete_one(
            UploadedFile.collection,
            {"_id": ObjectId(file_id)}
        )
        return result
