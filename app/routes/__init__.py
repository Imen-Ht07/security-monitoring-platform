from flask import Blueprint

def register_blueprints(app):
    from . import api
    app.register_blueprint(api.bp)
