from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models import LearningStyle, ChatHistory, Download
from app.services.chatbot_service import generate_adaptive_response
from app.services.adaptive_content_service import generate_learning_asset
from app.services.download_service import create_download_file


chat_bp = Blueprint("chat", __name__, url_prefix="/api/chat")


def _auto_generate_resources(user_id: int, style: str, topic: str, base_content: str) -> list[dict]:
    resources = []
    content_types = ["pdf", "audio", "task_sheet", "solution"]
    for ctype in content_types:
        asset_text = generate_learning_asset(style, ctype, topic, base_content)
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

    result["auto_resources"] = auto_resources
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
