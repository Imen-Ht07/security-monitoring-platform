"""
app/models/uploaded_file.py - Modèle pour les fichiers uploadés
"""
from services.mongodb_service import MongoDBService
from datetime import datetime

class UploadedFile:
    """Modèle pour gérer les fichiers uploadés dans MongoDB"""
    
    def __init__(self):
        self.mongo = MongoDBService()
        self.collection = "uploaded_files"
    
    def create(self, filename, size, file_type):
        """Crée une entrée fichier dans MongoDB
        
        Args:
            filename (str): Nom du fichier
            size (int): Taille en bytes
            file_type (str): Type (csv, json, txt, log)
            
        Returns:
            dict: Document MongoDB créé
        """
        doc = {
            "filename": filename,
            "size": size,
            "file_type": file_type,
            "uploaded_at": datetime.now(),
            "status": "processed"
        }
        result = self.mongo.insert_one(self.collection, doc)
        return {"_id": str(result.inserted_id)} if result else None
    
    def get_all(self):
        """Récupère tous les fichiers uploadés
        
        Returns:
            list: Liste des documents
        """
        docs = self.mongo.find_all(self.collection)
        # Convertir ObjectId en string
        for doc in docs:
            doc["_id"] = str(doc["_id"])
            if "uploaded_at" in doc:
                doc["uploaded_at"] = doc["uploaded_at"].isoformat()
        return docs
    
    def get_by_id(self, file_id):
        """Récupère un fichier par son ID
        
        Args:
            file_id (str): ID MongoDB
            
        Returns:
            dict: Document ou None
        """
        from bson import ObjectId
        try:
            doc = self.mongo.find_one(
                self.collection,
                {"_id": ObjectId(file_id)}
            )
            if doc:
                doc["_id"] = str(doc["_id"])
            return doc
        except:
            return None
    
    def get_recent(self, limit=10):
        """Récupère les fichiers uploadés récemment
        
        Args:
            limit (int): Nombre maximum
            
        Returns:
            list: Liste triée par date décroissante
        """
        docs = self.mongo.find_all(self.collection)
        docs = sorted(
            docs, 
            key=lambda x: x.get("uploaded_at", datetime.now()), 
            reverse=True
        )[:limit]
        
        for doc in docs:
            doc["_id"] = str(doc["_id"])
            if "uploaded_at" in doc:
                doc["uploaded_at"] = doc["uploaded_at"].isoformat()
        return docs
    
    def update_status(self, file_id, status):
        """Met à jour le statut d'un fichier
        
        Args:
            file_id (str): ID MongoDB
            status (str): Nouveau statut (processing, processed, failed)
            
        Returns:
            bool: True si succès
        """
        from bson import ObjectId
        try:
            self.mongo.db[self.collection].update_one(
                {"_id": ObjectId(file_id)},
                {"$set": {"status": status}}
            )
            return True
        except:
            return False
    
    def delete(self, file_id):
        """Supprime un fichier
        
        Args:
            file_id (str): ID MongoDB
            
        Returns:
            bool: True si succès
        """
        from bson import ObjectId
        try:
            self.mongo.db[self.collection].delete_one(
                {"_id": ObjectId(file_id)}
            )
            return True
        except:
            return False