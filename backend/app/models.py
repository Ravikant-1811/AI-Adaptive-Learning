from datetime import datetime, timedelta
import secrets
from app.extensions import db


class User(db.Model):
    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class LearningStyle(db.Model):
    __tablename__ = "learning_style"

    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), primary_key=True)
    learning_style = db.Column(db.String(20), nullable=False)  # visual/auditory/kinesthetic
    visual_score = db.Column(db.Integer, default=0, nullable=False)
    auditory_score = db.Column(db.Integer, default=0, nullable=False)
    kinesthetic_score = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class ChatHistory(db.Model):
    __tablename__ = "chat_history"

    chat_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False, index=True)
    question = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=False)
    response_type = db.Column(db.String(20), nullable=False)
    learning_style_used = db.Column(db.String(20), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class PracticeActivity(db.Model):
    __tablename__ = "practice_activity"

    activity_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False, index=True)
    task_name = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(40), default="started", nullable=False)
    code_submitted = db.Column(db.Text, nullable=True)
    time_spent = db.Column(db.Integer, default=0, nullable=False)  # seconds
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class Download(db.Model):
    __tablename__ = "downloads"

    download_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False, index=True)
    content_type = db.Column(db.String(50), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class PasswordResetToken(db.Model):
    __tablename__ = "password_reset_tokens"

    token = db.Column(db.String(128), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False, index=True)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    @staticmethod
    def create_for_user(user_id: int, ttl_minutes: int = 30) -> "PasswordResetToken":
        return PasswordResetToken(
            token=secrets.token_urlsafe(48),
            user_id=user_id,
            expires_at=datetime.utcnow() + timedelta(minutes=max(5, ttl_minutes)),
            used=False,
        )
