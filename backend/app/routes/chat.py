from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError
from app.extensions import db
from app.models import LearningStyle, ChatHistory, Download, ChatFeedback
from app.services.chatbot_service import generate_adaptive_response, get_quick_prompts
from app.services.download_service import create_download_file
from app.services.practice_task_service import generate_practice_tasks_from_topic
from app.services.adaptive_content_service import generate_learning_asset


chat_bp = Blueprint("chat", __name__, url_prefix="/api/chat")


def _auto_generate_resources(user_id: int, style: str, topic: str, base_content: str) -> list[dict]:
    resources = []
    # Generate per-type assets so task_sheet and solution are intentionally different.
    content_types = ["pdf", "task_sheet", "solution"]
    for ctype in content_types:
        generated = generate_learning_asset(
            style=style,
            content_type=ctype,
            topic=topic,
            base_content=base_content[:3500],
        )
        if ctype == "task_sheet":
            asset_text = (
                f"Topic: {topic}\n"
                f"Learning style: {style}\n"
                "Resource type: task_sheet\n\n"
                "Practice Task Sheet\n"
                "- Objective\n"
                "- Steps to implement\n"
                "- Test cases to run\n"
                "- Submission checklist\n\n"
                f"{generated}"
            )
        elif ctype == "solution":
            asset_text = (
                f"Topic: {topic}\n"
                f"Learning style: {style}\n"
                "Resource type: solution\n\n"
                "Worked Solution\n"
                "- Final code\n"
                "- Why this works\n"
                "- Expected output\n"
                "- Common mistakes avoided\n\n"
                f"{generated}"
            )
        else:
            asset_text = (
                f"Topic: {topic}\n"
                f"Learning style: {style}\n"
                f"Resource type: {ctype}\n\n"
                f"{generated}"
            )

        file_path = create_download_file(user_id, ctype, asset_text)
        row = Download(user_id=user_id, content_type=ctype, file_path=file_path)
        db.session.add(row)
        db.session.flush()
        resources.append(
            {
                "download_id": row.download_id,
                "content_type": ctype,
                "download_url": f"/api/downloads/file/{row.download_id}",
            }
        )
    return resources


@chat_bp.post("/")
@jwt_required()
def ask_chatbot():
    user_id = int(get_jwt_identity())
    question = (request.get_json() or {}).get("question", "").strip()
    if not question:
        return jsonify({"error": "question is required"}), 400

    style_row = LearningStyle.query.get(user_id)
    if not style_row:
        return jsonify({"error": "learning style not found"}), 400

    result = generate_adaptive_response(question, style_row.learning_style)
    # Generate topic-specific tasks; fallback logic inside service handles failures gracefully.
    practice_tasks, practice_source = generate_practice_tasks_from_topic(question, count=3, allow_ai=True)
    try:
        auto_resources = _auto_generate_resources(
            user_id=user_id,
            style=style_row.learning_style,
            topic=question,
            base_content=result["text"],
        )

        history = ChatHistory(
            user_id=user_id,
            question=question,
            response=result["text"],
            response_type=result["response_type"],
            learning_style_used=style_row.learning_style,
        )
        db.session.add(history)
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "temporary database issue. please retry"}), 503

    result["auto_resources"] = auto_resources
    result["chat_id"] = history.chat_id
    result["practice"] = {
        "topic": question,
        "source": practice_source,
        "tasks": practice_tasks,
    }
    return jsonify(result)


@chat_bp.get("/history")
@jwt_required()
def chat_history():
    user_id = int(get_jwt_identity())
    rows = (
        ChatHistory.query.filter_by(user_id=user_id)
        .order_by(ChatHistory.timestamp.desc())
        .limit(30)
        .all()
    )
    feedback_rows = []
    if rows:
        feedback_rows = ChatFeedback.query.filter(
            ChatFeedback.user_id == user_id,
            ChatFeedback.chat_id.in_([r.chat_id for r in rows]),
        ).all()
    feedback_map = {f.chat_id: {"rating": f.rating, "comment": f.comment} for f in feedback_rows}

    return jsonify(
        [
            {
                "chat_id": r.chat_id,
                "question": r.question,
                "response": r.response,
                "response_type": r.response_type,
                "learning_style_used": r.learning_style_used,
                "timestamp": r.timestamp.isoformat(),
                "feedback": feedback_map.get(r.chat_id),
            }
            for r in rows
        ]
    )


@chat_bp.get("/suggestions")
@jwt_required()
def chat_suggestions():
    user_id = int(get_jwt_identity())
    topic = (request.args.get("topic") or "").strip()
    style_row = LearningStyle.query.get(user_id)
    style = style_row.learning_style if style_row else "visual"
    prompts = get_quick_prompts(topic or "Java basics", style)
    return jsonify({"topic": topic or "Java basics", "prompts": prompts})


@chat_bp.delete("/history/<int:chat_id>")
@jwt_required()
def delete_chat_item(chat_id: int):
    user_id = int(get_jwt_identity())
    row = ChatHistory.query.filter_by(chat_id=chat_id, user_id=user_id).first()
    if not row:
        return jsonify({"error": "chat not found"}), 404
    ChatFeedback.query.filter_by(chat_id=chat_id, user_id=user_id).delete()
    db.session.delete(row)
    db.session.commit()
    return jsonify({"message": "chat deleted", "chat_id": chat_id})


@chat_bp.delete("/history")
@jwt_required()
def clear_history():
    user_id = int(get_jwt_identity())
    try:
        chat_ids = [r.chat_id for r in ChatHistory.query.filter_by(user_id=user_id).all()]
        if chat_ids:
            ChatFeedback.query.filter(
                ChatFeedback.user_id == user_id,
                ChatFeedback.chat_id.in_(chat_ids),
            ).delete(synchronize_session=False)
        ChatHistory.query.filter_by(user_id=user_id).delete()
        db.session.commit()
        return jsonify({"message": "chat history cleared"})
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "failed to clear chat history"}), 500


@chat_bp.post("/feedback")
@jwt_required()
def chat_feedback():
    user_id = int(get_jwt_identity())
    payload = request.get_json() or {}
    try:
        chat_id = int(payload.get("chat_id"))
    except (TypeError, ValueError):
        return jsonify({"error": "chat_id is required"}), 400

    try:
        rating = int(payload.get("rating"))
    except (TypeError, ValueError):
        return jsonify({"error": "rating must be 1 or -1"}), 400
    if rating not in {1, -1}:
        return jsonify({"error": "rating must be 1 or -1"}), 400

    comment = str(payload.get("comment", "")).strip()[:600]
    chat_row = ChatHistory.query.filter_by(chat_id=chat_id, user_id=user_id).first()
    if not chat_row:
        return jsonify({"error": "chat not found"}), 404

    row = ChatFeedback.query.filter_by(chat_id=chat_id, user_id=user_id).first()
    if not row:
        row = ChatFeedback(chat_id=chat_id, user_id=user_id, rating=rating, comment=comment or None)
        db.session.add(row)
    else:
        row.rating = rating
        row.comment = comment or None
    db.session.commit()
    return jsonify({"message": "feedback saved", "chat_id": chat_id, "rating": rating})
