from flask import Flask, render_template
from config import Config
from routes import register_blueprints
from db_init import init_mongodb
import logging

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app():
    """Crée et configure l'app Flask"""
    app = Flask(__name__, 
                template_folder="templates", 
                static_folder="static")
    
    # Charge la configuration
    app.config.from_object(Config)
    
    # 🔄 Initialiser MongoDB au démarrage
    logger.info("🚀 Initialisation de l'application...")
    init_mongodb()
    
    # Enregistre les blueprints
    register_blueprints(app)
    
    # Route principale
    @app.route("/")
    def index():
        return render_template("dashboard.html")
    
    logger.info("✅ Application initialisée avec succès !")
    
    return app

# Instance globale
app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)