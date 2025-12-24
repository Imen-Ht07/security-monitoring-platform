# app/routes/__init__.py
from flask import Blueprint

def register_blueprints(app):
    """
    Enregistre tous les blueprints de l'application
    """

    from app.routes.api_search import bp_search
    from app.routes.api_stats import bp_stats
    from app.routes.api_ingest import bp_ingest
    from app.routes.api_history import bp_history
    from app.routes.api_health import bp_health
    from app.routes.api_upload import upload_bp
    
    app.register_blueprint(upload_bp)
    app.register_blueprint(bp_search)
    app.register_blueprint(bp_stats)
    app.register_blueprint(bp_ingest)
    app.register_blueprint(bp_history)
    app.register_blueprint(bp_health)
