from flask import Flask, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from sqlalchemy import text

from config import Config
from models import db

migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Extensions
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app, resources={r"/api/*": {"origins": ["http://localhost:5173"]}})

    # Routes
    @app.get("/api/health")
    def health():
        try:
            db.session.execute(text("SELECT 1"))
            return jsonify(status="ok", database="ok"), 200

        except Exception as err:
            app.logger.error("Health check database error: %s", err)
            return jsonify(status="error", database="unreachable"), 500

    # JSON errors instead of Flask's default HTML pages
    @app.errorhandler(404)
    def not_found(_err):
        return jsonify(error="Not found"), 404

    return app