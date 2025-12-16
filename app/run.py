from flask import Flask, render_template
from config import Config
from routes import register_blueprints 

def create_app():
    """Crée et configure l'app Flask"""
    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static"
    )

    app.config.from_object(Config)
    register_blueprints(app)

    @app.route("/")
    def index():
        return render_template("dashboard.html")

    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
