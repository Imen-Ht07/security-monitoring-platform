from pymongo import MongoClient
from datetime import datetime
import os

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://admin:changeme@mongodb:27017")

class SearchHistory:
    def __init__(self):
        self.client = MongoClient(MONGODB_URL)
        self.db = self.client["security_logs"]
        self.collection = self.db["search_history"]

    def create(self, search_term, filters, num_results):
        """Enregistre une recherche effectuée"""
        document = {
            "search_term": search_term,
            "filters": filters,
            "num_results": num_results,
            "executed_at": datetime.utcnow()
        }
        result = self.collection.insert_one(document)
        return str(result.inserted_id)

    def get_recent(self, limit=10):
        """Récupère les dernières recherches"""
        searches = list(self.collection.find().sort("executed_at", -1).limit(limit))
        for s in searches:
            s["_id"] = str(s["_id"])
        return searches
