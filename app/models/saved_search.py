"""
app/models/saved_search.py
Modèle pour les recherches sauvegardées
"""
from datetime import datetime
from bson import ObjectId
from app.services.mongodb_service import MongoDBService
import logging

logger = logging.getLogger(__name__)

class SavedSearch:
    collection = "saved_searches"

    def __init__(
        self,
        name,
        description="",
        filters=None,
        id=None,
        created_at=None
    ):
        self.mongo = MongoDBService()
        self.id = id or ObjectId()
        self.name = name
        self.description = description
        self.filters = filters or {}
        self.created_at = created_at or datetime.now()

    # ================= CREATE =================
    def save(self):
        doc = {
            "_id": self.id,
            "name": self.name,
            "description": self.description,
            "filters": self.filters,
            "created_at": self.created_at
        }
        self.mongo.insert_one(self.collection, doc)
        logger.info(f"Saved search '{self.name}' created")
        return self

    # ================= GET BY ID =================
    @staticmethod
    def get_by_id(search_id):
        mongo = MongoDBService()
        try:
            doc = mongo.find_one(
                SavedSearch.collection,
                {"_id": ObjectId(search_id)}
            )
            if not doc:
                return None

            return SavedSearch(
                name=doc["name"],
                description=doc.get("description", ""),
                filters=doc.get("filters", {}),
                id=doc["_id"],
                created_at=doc["created_at"]
            )
        except Exception as e:
            logger.error(f"Get saved search error: {e}")
            return None

    # ================= GET ALL =================
    @staticmethod
    def get_all():
        mongo = MongoDBService()
        docs = mongo.find_all(SavedSearch.collection)

        results = []
        for doc in sorted(docs, key=lambda x: x["created_at"], reverse=True):
            results.append({
                "id": str(doc["_id"]),
                "name": doc["name"],
                "description": doc.get("description", ""),
                "filters": doc.get("filters", {}),
                "created_at": doc["created_at"].isoformat()
            })
        return results

    # ================= DELETE =================
    @staticmethod
    def delete_by_id(search_id):
        mongo = MongoDBService()
        result = mongo.delete_one(
            SavedSearch.collection,
            {"_id": ObjectId(search_id)}
        )
        logger.info(f"Saved search '{search_id}' deleted")
        return result
   # ================= GET RECENT =================
@staticmethod
def get_recent(limit=10):
    """Récupère les X dernières recherches"""
    mongo = MongoDBService()
    docs = mongo.find_all(
        SavedSearch.collection,
        sort=[('created_at', -1)],
        limit=limit
    )

    results = []
    for doc in docs:
        results.append({
            "id": str(doc["_id"]),
            "name": doc["name"],
            "description": doc.get("description", ""),
            "filters": doc.get("filters", {}),
            "created_at": doc["created_at"].isoformat()
        })
    return results

