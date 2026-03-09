import os
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from sqlalchemy import text
from app.config import build_runtime_config, cors_origins_from_env
from app.extensions import db, jwt


def create_app():
    load_dotenv()
    app = Flask(__name__)

    runtime = build_runtime_config()
    app.config.update(runtime)
    app_env = runtime["APP_ENV"]
    database_uri = runtime["SQLALCHEMY_DATABASE_URI"]

    cors_origins = cors_origins_from_env()
    CORS(
        app,
        resources={r"/api/*": {"origins": cors_origins}},
        supports_credentials=False,
    )

    db.init_app(app)
    jwt.init_app(app)

    from app.routes import register_blueprints

    register_blueprints(app)

    @app.get("/")
    def root():
        return {
            "name": "Adaptive AI Learning Platform API",
            "status": "ok",
            "env": app_env,
            "health": "/api/health",
            "ready": "/api/ready",
        }

    @app.get("/api/health")
    def health():
        return {"status": "ok"}

    @app.get("/api/ready")
    def ready():
        try:
            db.session.execute(text("SELECT 1"))
            db.session.commit()
            return {"status": "ready"}
        except Exception:
            db.session.rollback()
            return jsonify({"status": "not_ready"}), 503

    @app.errorhandler(404)
    def not_found(_):
        return jsonify({"error": "not found"}), 404

    @app.errorhandler(500)
    def server_error(_):
        return jsonify({"error": "internal server error"}), 500

    with app.app_context():
        from app import models

        db.create_all()
        if database_uri.startswith("sqlite"):
            db.session.execute(text("PRAGMA journal_mode=WAL"))
            db.session.execute(text("PRAGMA synchronous=NORMAL"))
            db.session.commit()

    return app
