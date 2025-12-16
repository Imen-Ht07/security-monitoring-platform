from pymongo import MongoClient
from config import Config

class MongoDBService:
    """Service pour MongoDB"""
    
    def __init__(self):
        client = MongoClient(Config.MONGODB_URL)
        self.db = client[Config.MONGODB_DB]
    
    def insert_one(self, collection, document):
        """Insère un document"""
        return self.db[collection].insert_one(document)
    
    def find_one(self, collection, query):
        """Cherche un document"""
        return self.db[collection].find_one(query)
    
    def find_all(self, collection, query=None):
        """Trouve tous les documents"""
        return list(self.db[collection].find(query or {}))