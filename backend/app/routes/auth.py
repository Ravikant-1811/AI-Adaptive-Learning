from datetime import datetime
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.extensions import db
from app.models import User, PasswordResetToken, LearningStyle, ChatHistory, PracticeActivity, Download


auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.post("/register")
def register():
    data = request.get_json() or {}
    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not name or not email or not password:
        return jsonify({"error": "name, email, and password are required"}), 400
    if len(password) < 6:
        return jsonify({"error": "password must be at least 6 characters"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "email already exists"}), 409

    user = User(name=name, email=email, password_hash=generate_password_hash(password))
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "registered successfully"}), 201


@auth_bp.post("/login")
def login():
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "invalid credentials"}), 401

    token = create_access_token(identity=str(user.user_id))
    return jsonify(
        {
            "access_token": token,
            "user": {
                "user_id": user.user_id,
                "name": user.name,
                "email": user.email,
            },
        }
    )


@auth_bp.get("/me")
@jwt_required()
def me():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "user not found"}), 404

    return jsonify({"user_id": user.user_id, "name": user.name, "email": user.email})


@auth_bp.put("/me")
@jwt_required()
def update_me():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "user not found"}), 404

    data = request.get_json() or {}
    if "name" in data:
        name = str(data.get("name", "")).strip()
        if not name:
            return jsonify({"error": "name cannot be empty"}), 400
        user.name = name

    if "email" in data:
        email = str(data.get("email", "")).strip().lower()
        if not email:
            return jsonify({"error": "email cannot be empty"}), 400
        existing = User.query.filter(User.email == email, User.user_id != user_id).first()
        if existing:
            return jsonify({"error": "email already exists"}), 409
        user.email = email

    if "password" in data:
        password = str(data.get("password", ""))
        if len(password) < 6:
            return jsonify({"error": "password must be at least 6 characters"}), 400
        user.password_hash = generate_password_hash(password)

    db.session.commit()
    return jsonify({"message": "profile updated", "user": {"user_id": user.user_id, "name": user.name, "email": user.email}})


@auth_bp.post("/logout")
@jwt_required()
def logout():
    return jsonify({"message": "logout successful on client token removal"})


@auth_bp.delete("/me")
@jwt_required()
def delete_me():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "user not found"}), 404

    ChatHistory.query.filter_by(user_id=user_id).delete()
    PracticeActivity.query.filter_by(user_id=user_id).delete()
    Download.query.filter_by(user_id=user_id).delete()
    LearningStyle.query.filter_by(user_id=user_id).delete()
    PasswordResetToken.query.filter_by(user_id=user_id).delete()
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "account deleted"})


@auth_bp.post("/forgot-password")
def forgot_password():
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()
    if not email:
        return jsonify({"error": "email is required"}), 400

    user = User.query.filter_by(email=email).first()
    # Avoid account enumeration by returning a success response in all cases.
    if not user:
        return jsonify({"message": "If email exists, reset instructions were generated."})

    token_row = PasswordResetToken.create_for_user(user.user_id, ttl_minutes=30)
    db.session.add(token_row)
    db.session.commit()
    return jsonify(
        {
            "message": "Password reset token generated.",
            "reset_token": token_row.token,
        }
    )


@auth_bp.post("/reset-password")
def reset_password():
    data = request.get_json() or {}
    token = data.get("token", "").strip()
    new_password = data.get("new_password", "")

    if not token or not new_password:
        return jsonify({"error": "token and new_password are required"}), 400
    if len(new_password) < 6:
        return jsonify({"error": "new_password must be at least 6 characters"}), 400

    token_row = PasswordResetToken.query.filter_by(token=token, used=False).first()
    if not token_row:
        return jsonify({"error": "invalid or used reset token"}), 400
    if token_row.expires_at < datetime.utcnow():
        return jsonify({"error": "reset token has expired"}), 400

    user = User.query.get(token_row.user_id)
    if not user:
        return jsonify({"error": "user not found"}), 404

    user.password_hash = generate_password_hash(new_password)
    token_row.used = True
    db.session.commit()
    return jsonify({"message": "password reset successful"})
