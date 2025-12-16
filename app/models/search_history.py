from services.mongodb_service import MongoDBService
from datetime import datetime

class SearchHistory:
    """Modèle pour l'historique de recherche"""
    
    def __init__(self):
        self.mongo = MongoDBService()
        self.collection = "search_history"
    
    def create(self, search_term, filters, num_results):
        """Enregistre une recherche"""
        doc = {
            "search_term": search_term,
            "filters": filters,
            "num_results": num_results,
            "searched_at": datetime.now()
        }
        return self.mongo.insert_one(self.collection, doc)
    
    def get_recent(self, limit=10):
        """Récupère les recherches récentes"""
        return self.mongo.find_all(
            self.collection,
            query={}
        )[-limit:]