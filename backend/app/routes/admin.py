from datetime import datetime, timedelta

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func

from app.extensions import db
from app.models import User, LearningStyle, ChatHistory, PracticeActivity, Download, ChatFeedback
from app.services.admin_auth import is_admin_email
from app.services.user_cleanup import delete_user_with_related_data


admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")


def _require_admin():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return None, (jsonify({"error": "user not found"}), 404)
    if not is_admin_email(user.email):
        return None, (jsonify({"error": "admin access required"}), 403)
    return user, None


@admin_bp.get("/summary")
@jwt_required()
def summary():
    _, err = _require_admin()
    if err:
        return err

    users_count = db.session.query(func.count(User.user_id)).scalar() or 0
    style_count = db.session.query(func.count(LearningStyle.user_id)).scalar() or 0
    chats_count = db.session.query(func.count(ChatHistory.chat_id)).scalar() or 0
    practice_count = db.session.query(func.count(PracticeActivity.activity_id)).scalar() or 0
    downloads_count = db.session.query(func.count(Download.download_id)).scalar() or 0

    latest_users = (
        User.query.order_by(User.created_at.desc()).limit(8).all()
    )
    latest_chats = (
        ChatHistory.query.order_by(ChatHistory.timestamp.desc()).limit(8).all()
    )
    return jsonify(
        {
            "metrics": {
                "users": users_count,
                "learning_styles": style_count,
                "chat_messages": chats_count,
                "practice_submissions": practice_count,
                "downloads": downloads_count,
            },
            "latest_users": [
                {
                    "user_id": u.user_id,
                    "name": u.name,
                    "email": u.email,
                    "created_at": u.created_at.isoformat(),
                    "is_admin": is_admin_email(u.email),
                }
                for u in latest_users
            ],
            "latest_chats": [
                {
                    "chat_id": c.chat_id,
                    "user_id": c.user_id,
                    "question": c.question,
                    "response_type": c.response_type,
                    "timestamp": c.timestamp.isoformat(),
                }
                for c in latest_chats
            ],
        }
    )


@admin_bp.get("/users")
@jwt_required()
def users():
    _, err = _require_admin()
    if err:
        return err

    query = User.query
    q = (request.args.get("q") or "").strip().lower()
    if q:
        pattern = f"%{q}%"
        query = query.filter((User.name.ilike(pattern)) | (User.email.ilike(pattern)))

    rows = query.order_by(User.created_at.desc()).limit(200).all()
    result = []
    for u in rows:
        style = LearningStyle.query.get(u.user_id)
        chats = db.session.query(func.count(ChatHistory.chat_id)).filter(ChatHistory.user_id == u.user_id).scalar() or 0
        downloads = db.session.query(func.count(Download.download_id)).filter(Download.user_id == u.user_id).scalar() or 0
        practice = db.session.query(func.count(PracticeActivity.activity_id)).filter(PracticeActivity.user_id == u.user_id).scalar() or 0
        result.append(
            {
                "user_id": u.user_id,
                "name": u.name,
                "email": u.email,
                "is_admin": is_admin_email(u.email),
                "learning_style": style.learning_style if style else None,
                "created_at": u.created_at.isoformat(),
                "stats": {
                    "chats": chats,
                    "downloads": downloads,
                    "practice": practice,
                },
            }
        )
    return jsonify(result)


@admin_bp.delete("/users/<int:user_id>")
@jwt_required()
def delete_user(user_id: int):
    admin_user, err = _require_admin()
    if err:
        return err
    if admin_user.user_id == user_id:
        return jsonify({"error": "cannot delete own admin account"}), 400

    target = User.query.get(user_id)
    if not target:
        return jsonify({"error": "user not found"}), 404

    delete_user_with_related_data(user_id)
    return jsonify({"message": "user deleted", "user_id": user_id})


@admin_bp.get("/analytics")
@jwt_required()
def analytics():
    _, err = _require_admin()
    if err:
        return err

    # style distribution
    style_rows = (
        db.session.query(LearningStyle.learning_style, func.count(LearningStyle.user_id))
        .group_by(LearningStyle.learning_style)
        .all()
    )
    style_dist = {row[0]: row[1] for row in style_rows}

    # last 7-day trends
    today = datetime.utcnow().date()
    labels = [(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(6, -1, -1)]
    signup_map = {k: 0 for k in labels}
    chat_map = {k: 0 for k in labels}
    feedback_map = {k: 0 for k in labels}

    for row in User.query.filter(User.created_at >= datetime.utcnow() - timedelta(days=7)).all():
        key = row.created_at.strftime("%Y-%m-%d")
        if key in signup_map:
            signup_map[key] += 1
    for row in ChatHistory.query.filter(ChatHistory.timestamp >= datetime.utcnow() - timedelta(days=7)).all():
        key = row.timestamp.strftime("%Y-%m-%d")
        if key in chat_map:
            chat_map[key] += 1
    for row in ChatFeedback.query.filter(ChatFeedback.created_at >= datetime.utcnow() - timedelta(days=7)).all():
        key = row.created_at.strftime("%Y-%m-%d")
        if key in feedback_map:
            feedback_map[key] += 1

    feedback_total = db.session.query(func.count(ChatFeedback.feedback_id)).scalar() or 0
    helpful = db.session.query(func.count(ChatFeedback.feedback_id)).filter(ChatFeedback.rating == 1).scalar() or 0
    needs_work = db.session.query(func.count(ChatFeedback.feedback_id)).filter(ChatFeedback.rating == -1).scalar() or 0
    avg_rating = 0
    if feedback_total:
        avg_rating = round(((helpful - needs_work) / feedback_total), 2)

    return jsonify(
        {
            "style_distribution": style_dist,
            "daily_signups": [{"date": d, "count": signup_map[d]} for d in labels],
            "daily_chats": [{"date": d, "count": chat_map[d]} for d in labels],
            "daily_feedback": [{"date": d, "count": feedback_map[d]} for d in labels],
            "feedback_summary": {
                "total": feedback_total,
                "helpful": helpful,
                "needs_work": needs_work,
                "avg_rating": avg_rating,
            },
        }
    )
