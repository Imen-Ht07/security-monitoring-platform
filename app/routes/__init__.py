def register_blueprints(app):
    """Enregistre tous les blueprints"""
    from . import api
    app.register_blueprint(api.bp)
