from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError
from app.extensions import db
from app.models import LearningStyle, ChatHistory, Download
from app.services.chatbot_service import generate_adaptive_response
from app.services.download_service import create_download_file
from app.services.practice_task_service import generate_practice_tasks_from_topic


chat_bp = Blueprint("chat", __name__, url_prefix="/api/chat")


def _auto_generate_resources(user_id: int, style: str, topic: str, base_content: str) -> list[dict]:
    resources = []
    # Keep chat response fast and stable by generating lightweight assets synchronously.
    # Audio can still be generated explicitly from the Downloads module on demand.
    content_types = ["pdf", "task_sheet", "solution"]
    for ctype in content_types:
        asset_text = (
            f"Topic: {topic}\n"
            f"Learning style: {style}\n"
            f"Resource type: {ctype}\n\n"
            f"{base_content[:3500]}"
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
    practice_tasks, practice_source = generate_practice_tasks_from_topic(question, count=3)
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
    return jsonify(
        [
            {
                "chat_id": r.chat_id,
                "question": r.question,
                "response": r.response,
                "response_type": r.response_type,
                "learning_style_used": r.learning_style_used,
                "timestamp": r.timestamp.isoformat(),
            }
            for r in rows
        ]
    )


@chat_bp.delete("/history")
@jwt_required()
def clear_history():
    user_id = int(get_jwt_identity())
    try:
        ChatHistory.query.filter_by(user_id=user_id).delete()
        db.session.commit()
        return jsonify({"message": "chat history cleared"})
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "failed to clear chat history"}), 500
