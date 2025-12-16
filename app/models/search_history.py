"""
app/models/search_history.py - Modèle pour l'historique des recherches
"""
from services.mongodb_service import MongoDBService
from datetime import datetime

class SearchHistory:
    """Modèle pour gérer l'historique des recherches dans MongoDB"""
    
    def __init__(self):
        self.mongo = MongoDBService()
        self.collection = "search_history"
    
    def create(self, search_term, filters, num_results):
        """Enregistre une recherche dans MongoDB
        
        Args:
            search_term (str): Terme recherché
            filters (dict): Filtres appliqués
            num_results (int): Nombre de résultats trouvés
            
        Returns:
            dict: Document créé
        """
        doc = {
            "search_term": search_term,
            "filters": filters,
            "num_results": num_results,
            "searched_at": datetime.now()
        }
        result = self.mongo.insert_one(self.collection, doc)
        return {"_id": str(result.inserted_id)} if result else None
    
    def get_recent(self, limit=10):
        """Récupère les recherches récentes
        
        Args:
            limit (int): Nombre maximum (défaut: 10)
            
        Returns:
            list: Liste triée par date décroissante
        """
        docs = self.mongo.find_all(self.collection)
        
        # Trier par date décroissante
        docs = sorted(
            docs,
            key=lambda x: x.get("searched_at", datetime.now()),
            reverse=True
        )[:limit]
        
        # Convertir ObjectId et dates en string pour JSON
        for doc in docs:
            doc["_id"] = str(doc["_id"])
            if "searched_at" in doc:
                doc["searched_at"] = doc["searched_at"].isoformat()
        
        return docs
    
    def get_by_term(self, search_term):
        """Récupère les recherches pour un terme spécifique
        
        Args:
            search_term (str): Terme recherché
            
        Returns:
            list: Liste des recherches correspondantes
        """
        docs = self.mongo.find_all(
            self.collection,
            {"search_term": search_term}
        )
        
        for doc in docs:
            doc["_id"] = str(doc["_id"])
            if "searched_at" in doc:
                doc["searched_at"] = doc["searched_at"].isoformat()
        
        return docs
    
    def get_stats(self):
        """Récupère les statistiques de recherche
        
        Returns:
            dict: Stats (total, top_terms, avg_results)
        """
        docs = self.mongo.find_all(self.collection)
        
        if not docs:
            return {
                "total_searches": 0,
                "top_terms": [],
                "avg_results": 0
            }
        
        # Compter les recherches par terme
        term_counts = {}
        total_results = 0
        
        for doc in docs:
            term = doc.get("search_term", "")
            if term:
                term_counts[term] = term_counts.get(term, 0) + 1
            total_results += doc.get("num_results", 0)
        
        # Top 5 termes
        top_terms = sorted(
            term_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        return {
            "total_searches": len(docs),
            "top_terms": [{"term": t[0], "count": t[1]} for t in top_terms],
            "avg_results": round(total_results / len(docs), 2) if docs else 0
        }
    
    def delete_old(self, days=30):
        """Supprime les recherches plus anciennes que N jours
        
        Args:
            days (int): Nombre de jours (défaut: 30)
            
        Returns:
            int: Nombre de documents supprimés
        """
        from datetime import timedelta
        cutoff_date = datetime.now() - timedelta(days=days)
        
        result = self.mongo.db[self.collection].delete_many(
            {"searched_at": {"$lt": cutoff_date}}
        )
        return result.deleted_count if result else 0