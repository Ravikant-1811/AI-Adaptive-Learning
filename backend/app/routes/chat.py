from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models import LearningStyle, ChatHistory
from app.services.chatbot_service import generate_adaptive_response


chat_bp = Blueprint("chat", __name__, url_prefix="/api/chat")


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
    history = ChatHistory(
        user_id=user_id,
        question=question,
        response=result["text"],
        response_type=result["response_type"],
        learning_style_used=style_row.learning_style,
    )
    db.session.add(history)
    db.session.commit()

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
