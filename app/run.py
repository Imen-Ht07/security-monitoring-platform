from flask import Flask, render_template
import os
from dotenv import load_dotenv
import logging

# Charger les variables d'env
load_dotenv()

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app(config_name=None):
    """Crée et configure l'app Flask"""
    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "development")
    
    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static"
    )
    
    # Charger la configuration
    if config_name == "production":
        from config import ProductionConfig
        app. config.from_object(ProductionConfig)
    elif config_name == "testing":
        from config import TestingConfig
        app.config.from_object(TestingConfig)
    else:
        from config import DevelopmentConfig
        app.config.from_object(DevelopmentConfig)
    
    logger.info(f"🚀 Application démarrée en mode {config_name}")
    
    # Route principale
    @app.route("/")
    def index():
        return render_template("dashboard.html")
    
    # Health check basique
    @app.route("/health")
    def health():
        return {"status": "healthy", "version": "0.1.0"}, 200
    
    logger.info("✅ Application initialisée avec succès !")
    
    return app

# Instance globale pour Gunicorn
app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)