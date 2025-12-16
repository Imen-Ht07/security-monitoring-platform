from services.mongodb_service import MongoDBService
from datetime import datetime

class UploadedFile:
    """Modèle pour les fichiers uploadés"""
    
    def __init__(self):
        self.mongo = MongoDBService()
        self.collection = "uploaded_files"
    
    def create(self, filename, size, file_type):
        """Crée une entrée fichier"""
        doc = {
            "filename": filename,
            "size": size,
            "file_type": file_type,
            "uploaded_at": datetime.now(),
            "status": "processed"
        }
        return self.mongo.insert_one(self.collection, doc)
    
    def get_all(self):
        """Récupère tous les fichiers"""
        return self.mongo.find_all(self.collection)