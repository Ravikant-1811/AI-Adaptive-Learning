import os


def is_truthy(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def cors_origins_from_env() -> list[str] | str:
    raw = os.getenv("CORS_ORIGINS", "*").strip()
    if raw == "*":
        return "*"
    origins = [item.strip() for item in raw.split(",") if item.strip()]
    return origins or "*"


def build_runtime_config() -> dict:
    app_env = os.getenv("APP_ENV", "development").strip().lower()
    is_production = app_env == "production"

    secret_key = os.getenv("SECRET_KEY", "dev-secret")
    jwt_secret = os.getenv("JWT_SECRET_KEY", "dev-jwt-secret")
    if is_production and (secret_key == "dev-secret" or jwt_secret == "dev-jwt-secret"):
        raise RuntimeError("Production requires strong SECRET_KEY and JWT_SECRET_KEY values")

    database_uri = os.getenv("DATABASE_URL", "sqlite:///adaptive_learning.db")

    config = {
        "APP_ENV": app_env,
        "SECRET_KEY": secret_key,
        "JWT_SECRET_KEY": jwt_secret,
        "JWT_ACCESS_TOKEN_EXPIRES": int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES_SECONDS", "86400")),
        "SQLALCHEMY_DATABASE_URI": database_uri,
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
    }

    if database_uri.startswith("sqlite"):
        config["SQLALCHEMY_ENGINE_OPTIONS"] = {
            "connect_args": {
                "timeout": int(os.getenv("SQLITE_TIMEOUT_SECONDS", "30")),
                "check_same_thread": False,
            }
        }

    return config
