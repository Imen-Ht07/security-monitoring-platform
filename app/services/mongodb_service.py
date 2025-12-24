# app/services/mongodb_service.py
import os
import logging
from pymongo import MongoClient
from dotenv import load_dotenv

# Charger les variables d'environnement depuis .env
load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class MongoDBService:
    """Service centralisé pour MongoDB"""

    def __init__(self):
        mongo_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
        mongo_db = os.getenv("MONGODB_DB", "default_db")

        try:
            self.client = MongoClient(
                mongo_url,
                serverSelectionTimeoutMS=5000
            )
            self.db = self.client[mongo_db]
            logger.info(f"🔗 Connecté à MongoDB sur {mongo_url}, DB={mongo_db}")
        except Exception as e:
            logger.error(f"❌ Erreur connexion MongoDB: {e}")
            raise

    # ================= INSERT =================
    def insert_one(self, collection, document):
        return self.db[collection].insert_one(document)

    # ================= FIND =================
    def find_one(self, collection, query):
        return self.db[collection].find_one(query)

    def find_all(self, collection, query=None, sort=None, limit=None):
        cursor = self.db[collection].find(query or {})

        if sort:
            cursor = cursor.sort(sort)

        if limit:
            cursor = cursor.limit(limit)

        return list(cursor)

    # ================= DELETE =================
    def delete_one(self, collection, query):
        return self.db[collection].delete_one(query)

    def delete_many(self, collection, query):
        return self.db[collection].delete_many(query)

    # ================= UPDATE =================
    def update_one(self, collection, query, update):
        return self.db[collection].update_one(query, update)

    # ================= UTILS =================
    def count(self, collection, query=None):
        return self.db[collection].count_documents(query or {})

    def ping(self):
        """Vérifie la connexion MongoDB"""
        try:
            self.client.admin.command("ping")
            logger.info("✅ MongoDB ping successful")
            return True
        except Exception as e:
            logger.error(f"MongoDB ping failed: {e}")
            return False
