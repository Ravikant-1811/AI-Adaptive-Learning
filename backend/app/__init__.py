import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
from sqlalchemy import text
from app.extensions import db, jwt


def create_app():
    load_dotenv()
    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret")
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "dev-jwt-secret")
    database_uri = os.getenv("DATABASE_URL", "sqlite:///adaptive_learning.db")
    app.config["SQLALCHEMY_DATABASE_URI"] = database_uri
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    if database_uri.startswith("sqlite"):
        app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
            "connect_args": {
                "timeout": 30,
                "check_same_thread": False,
            }
        }

    CORS(app)
    db.init_app(app)
    jwt.init_app(app)

    from app.routes.auth import auth_bp
    from app.routes.style import style_bp
    from app.routes.chat import chat_bp
    from app.routes.practice import practice_bp
    from app.routes.download import download_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(style_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(practice_bp)
    app.register_blueprint(download_bp)

    @app.get("/api/health")
    def health():
        return {"status": "ok"}

    @app.get("/")
    def root():
        return {
            "name": "Adaptive AI Learning Platform API",
            "status": "ok",
            "health": "/api/health",
        }

    with app.app_context():
        from app import models

        db.create_all()
        if database_uri.startswith("sqlite"):
            db.session.execute(text("PRAGMA journal_mode=WAL"))
            db.session.execute(text("PRAGMA synchronous=NORMAL"))
            db.session.commit()

    return app
