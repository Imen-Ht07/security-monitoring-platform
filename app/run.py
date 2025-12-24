"""
app/__init__.py
Security Monitoring Platform - Flask App Factory
"""
import os
import sys
import logging
from flask import Flask, render_template
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_app():
    """Crée et configure l'app Flask"""
    logger.info("🚀 Initialisation de l'application...")
    
    app = Flask(__name__, 
                template_folder="templates", 
                static_folder="static")
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "dev-secret-key")
    app.config['DEBUG'] = os.getenv("FLASK_ENV") == "development"
    app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB
    
    # CORS
    CORS(app, resources={
        "/api/*": {
            "origins": ["*"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Routes principales
    @app.route("/")
    def index():
        try:
            return render_template("index.html")
        except:
            return {
                "message": "Security Monitoring Platform",
                "version": "1.0.0",
                "status": "running"
            }, 200
    
    @app.route("/api/health")
    def health():
        return {"status": "healthy", "service": "webapp"}, 200
    
    # Blueprints - Charger après création de l'app
    try:
        logger.info("📚 Enregistrement des blueprints...")
        
        # Ajouter le chemin parent pour importer 'routes'
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)
        
        from routes import register_blueprints
        register_blueprints(app)
        
        logger.info("✅ Blueprints enregistrés")
    except ImportError as e:
        logger.warning(f"⚠️ Blueprints import failed: {e}")
    except Exception as e:
        logger.warning(f"⚠️ Error registering blueprints: {e}")
    
    # MongoDB init
    try:
        logger.info("📊 Initialisation MongoDB...")
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)
        
        from db_init import init_mongodb
        init_mongodb()
        logger.info("✅ MongoDB initialisé")
    except ImportError:
        logger.warning("⚠️ db_init non trouvé (optionnel)")
    except Exception as e:
        logger.warning(f"⚠️ MongoDB init failed: {e}")
    
    logger.info("✅ Application initialisée avec succès!")
    return app


# ✅ Crée l'instance de l'app pour Gunicorn
app = create_app()

# ✅ Pour développement local
if __name__ == "__main__":
    host = os.getenv("FLASK_HOST", "0.0.0.0")
    port = int(os.getenv("FLASK_PORT", 8000))
    debug = os.getenv("FLASK_ENV") == "development"
    
    logger.info(f"🌐 Running on http://{host}:{port}")
    logger.info(f"📝 Debug mode: {debug}")
    
    app.run(host=host, port=port, debug=debug)