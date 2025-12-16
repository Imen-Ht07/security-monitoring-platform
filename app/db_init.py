"""
app/db_init.py - Initialisation des collections MongoDB au démarrage
"""
from pymongo import MongoClient
from config import Config
import logging

logger = logging.getLogger(__name__)

def init_mongodb():
    """Initialise les collections MongoDB et les indices"""
    try:
        client = MongoClient(Config.MONGODB_URL)
        db = client[Config.MONGODB_DB]
        
        logger.info("🔄 Initialisation MongoDB...")
        
        # ===== Collection uploaded_files =====
        if "uploaded_files" not in db.list_collection_names():
            db.create_collection("uploaded_files")
            logger.info("✅ Collection 'uploaded_files' créée")
        
        # Créer les indices pour uploaded_files
        try:
            db.uploaded_files.create_index([("uploaded_at", -1)])
            db.uploaded_files.create_index([("filename", 1)])
            db.uploaded_files.create_index([("status", 1)])
            logger.info("✅ Indices 'uploaded_files' créés")
        except Exception as e:
            logger.warning(f"⚠️  Indices 'uploaded_files' peut-être déjà existants: {str(e)}")
        
        # ===== Collection search_history =====
        if "search_history" not in db.list_collection_names():
            db.create_collection("search_history")
            logger.info("✅ Collection 'search_history' créée")
        
        # Créer les indices pour search_history
        try:
            db.search_history.create_index([("searched_at", -1)])
            db.search_history.create_index([("search_term", 1)])
            db.search_history.create_index([("num_results", 1)])
            logger.info("✅ Indices 'search_history' créés")
        except Exception as e:
            logger.warning(f"⚠️  Indices 'search_history' peut-être déjà existants: {str(e)}")
        
        # ===== Vérification =====
        collections = db.list_collection_names()
        logger.info(f"📊 Collections dans '{Config.MONGODB_DB}': {collections}")
        
        # Document test dans uploaded_files
        uploaded_count = db.uploaded_files.count_documents({})
        logger.info(f"📈 Documents dans 'uploaded_files': {uploaded_count}")
        
        # Document test dans search_history
        history_count = db.search_history.count_documents({})
        logger.info(f"📈 Documents dans 'search_history': {history_count}")
        
        logger.info("✅ MongoDB initialisé avec succès !")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'initialisation MongoDB: {str(e)}")
        return False