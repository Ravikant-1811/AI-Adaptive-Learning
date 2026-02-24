import os
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from sqlalchemy import text
from app.extensions import db, jwt


def _is_truthy(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _cors_origins_from_env() -> list[str] | str:
    raw = os.getenv("CORS_ORIGINS", "*").strip()
    if raw == "*":
        return "*"
    origins = [item.strip() for item in raw.split(",") if item.strip()]
    return origins or "*"


def create_app():
    load_dotenv()
    app = Flask(__name__)

    app_env = os.getenv("APP_ENV", "development").strip().lower()
    is_production = app_env == "production"

    secret_key = os.getenv("SECRET_KEY", "dev-secret")
    jwt_secret = os.getenv("JWT_SECRET_KEY", "dev-jwt-secret")
    if is_production and (secret_key == "dev-secret" or jwt_secret == "dev-jwt-secret"):
        raise RuntimeError("Production requires strong SECRET_KEY and JWT_SECRET_KEY values")

    app.config["SECRET_KEY"] = secret_key
    app.config["JWT_SECRET_KEY"] = jwt_secret
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES_SECONDS", "86400"))

    database_uri = os.getenv("DATABASE_URL", "sqlite:///adaptive_learning.db")
    app.config["SQLALCHEMY_DATABASE_URI"] = database_uri
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    if database_uri.startswith("sqlite"):
        app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
            "connect_args": {
                "timeout": int(os.getenv("SQLITE_TIMEOUT_SECONDS", "30")),
                "check_same_thread": False,
            }
        }

    cors_origins = _cors_origins_from_env()
    CORS(
        app,
        resources={r"/api/*": {"origins": cors_origins}},
        supports_credentials=False,
    )

    db.init_app(app)
    jwt.init_app(app)

    from app.routes.auth import auth_bp
    from app.routes.style import style_bp
    from app.routes.chat import chat_bp
    from app.routes.practice import practice_bp
    from app.routes.download import download_bp
    from app.routes.admin import admin_bp
    from app.routes.dashboard import dashboard_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(style_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(practice_bp)
    app.register_blueprint(download_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(dashboard_bp)

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
