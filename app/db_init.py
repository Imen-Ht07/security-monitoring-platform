"""
app/db_init.py - Initialisation des collections MongoDB au démarrage
"""
import os
from pymongo import MongoClient
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Charger les variables d'environnement depuis .env
load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL")
MONGODB_DB = os.getenv("MONGODB_DB", "default_db")  # "default_db" si non défini

def init_mongodb():
    """Initialise les collections MongoDB et les indices"""
    try:
        client = MongoClient(MONGODB_URL)
        db = client[MONGODB_DB]
        
        logger.info("🔄 Initialisation MongoDB...")
        
        # ===== Collection uploaded_files =====
        if "uploaded_files" not in db.list_collection_names():
            db.create_collection("uploaded_files")
            logger.info("✅ Collection 'uploaded_files' créée")
        
        db.uploaded_files.create_index([("uploaded_at", -1)])
        db.uploaded_files.create_index([("filename", 1)])
        db.uploaded_files.create_index([("status", 1)])
        logger.info("✅ Indices 'uploaded_files' créés")
        
        # ===== Collection search_history =====
        if "search_history" not in db.list_collection_names():
            db.create_collection("search_history")
            logger.info("✅ Collection 'search_history' créée")
        
        db.search_history.create_index([("searched_at", -1)])
        db.search_history.create_index([("search_term", 1)])
        db.search_history.create_index([("num_results", 1)])
        logger.info("✅ Indices 'search_history' créés")
        
        # Vérification
        collections = db.list_collection_names()
        logger.info(f"📊 Collections dans '{MONGODB_DB}': {collections}")
        
        uploaded_count = db.uploaded_files.count_documents({})
        history_count = db.search_history.count_documents({})
        logger.info(f"📈 Documents dans 'uploaded_files': {uploaded_count}")
        logger.info(f"📈 Documents dans 'search_history': {history_count}")
        
        logger.info("✅ MongoDB initialisé avec succès !")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'initialisation MongoDB: {str(e)}")
        return False

if __name__ == "__main__":
    init_mongodb()
