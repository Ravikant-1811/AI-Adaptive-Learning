from pathlib import Path
from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models import Download, LearningStyle, ChatHistory
from app.services.adaptive_content_service import generate_learning_asset, generate_openai_solution
from app.services.download_service import create_download_file


download_bp = Blueprint("download", __name__, url_prefix="/api/downloads")


def _build_distinct_kinesthetic_asset(content_type: str, topic: str, generated: str) -> str:
    topic_line = f"Topic: {topic}"
    if content_type == "task_sheet":
        return "\n".join([
            topic_line,
            "Document Type: TASK SHEET",
            "",
            "Goal:",
            "Complete the implementation task step-by-step.",
            "",
            "Instructions:",
            "1) Read the problem and required exception flow.",
            "2) Write Java code from starter structure.",
            "3) Run at least two test cases (success + failure).",
            "4) Submit final code with brief notes.",
            "",
            "Checklist:",
            "- Uses try/catch/finally correctly",
            "- Handles error case with user-friendly message",
            "- Produces expected output",
            "",
            generated,
        ])

    return "\n".join([
        topic_line,
        "Document Type: WORKED SOLUTION",
        "",
        "Final Approach:",
        "Provide a complete solution with reasoning and expected output.",
        "",
        "Solution Structure:",
        "1) Final code",
        "2) Line-by-line explanation",
        "3) Expected output",
        "4) Why this handles exceptions safely",
        "",
        "Review Notes:",
        "- Mention common mistakes",
        "- Mention improvements/refactor options",
        "",
        generated,
    ])


@download_bp.post("/")
@jwt_required()
def create_download():
    user_id = int(get_jwt_identity())
    payload = request.get_json() or {}
    content_type = payload.get("content_type", "").strip()
    content = payload.get("content", "")
    base_content = str(payload.get("base_content", "")).strip()
    topic = str(payload.get("topic", "")).strip()

    style_row = LearningStyle.query.get(user_id)
    if not style_row:
        return jsonify({"error": "learning style not set"}), 400

    common_types = {"task_sheet", "solution", "pdf", "audio"}
    allowed_by_style = {
        "visual": {"pdf", "video"} | common_types,
        "auditory": {"audio"} | common_types,
        "kinesthetic": {"task_sheet", "solution"} | common_types,
    }

    if content_type not in allowed_by_style[style_row.learning_style]:
        return jsonify({"error": f"{content_type} is not allowed for {style_row.learning_style}"}), 400

    if not topic:
        latest_chat = (
            ChatHistory.query.filter_by(user_id=user_id)
            .order_by(ChatHistory.timestamp.desc())
            .first()
        )
        topic = latest_chat.question if latest_chat else "learning concept"

    base_payload = base_content or str(content or "").strip()

    if content_type == "solution":
        generated = generate_openai_solution(topic, base_payload)
        content = _build_distinct_kinesthetic_asset("solution", topic, generated)
    elif content_type == "task_sheet":
        generated = generate_learning_asset(style_row.learning_style, "task_sheet", topic, base_payload)
        content = _build_distinct_kinesthetic_asset("task_sheet", topic, generated)
    elif not str(content).strip():
        content = generate_learning_asset(style_row.learning_style, content_type, topic, base_payload)

    file_path = create_download_file(user_id, content_type, content)
    row = Download(user_id=user_id, content_type=content_type, file_path=file_path)
    db.session.add(row)
    db.session.commit()

    return jsonify(
        {
            "message": "download generated",
            "file_path": file_path,
            "download_id": row.download_id,
            "download_url": f"/api/downloads/file/{row.download_id}",
        }
    )


@download_bp.get("/file/<int:download_id>")
@jwt_required()
def fetch_download(download_id: int):
    user_id = int(get_jwt_identity())
    row = Download.query.filter_by(download_id=download_id, user_id=user_id).first()
    if not row:
        return jsonify({"error": "download not found"}), 404

    file_path = Path(row.file_path)
    if not file_path.exists() or not file_path.is_file():
        return jsonify({"error": "file missing"}), 404

    return send_file(file_path, as_attachment=True)


@download_bp.get("/mine")
@jwt_required()
def my_downloads():
    user_id = int(get_jwt_identity())
    rows = Download.query.filter_by(user_id=user_id).order_by(Download.timestamp.desc()).limit(50).all()
    return jsonify(
        [
            {
                "download_id": r.download_id,
                "content_type": r.content_type,
                "file_path": r.file_path,
                "download_url": f"/api/downloads/file/{r.download_id}",
                "timestamp": r.timestamp.isoformat(),
            }
            for r in rows
        ]
    )


@download_bp.get("/mine/<int:download_id>")
@jwt_required()
def get_download(download_id: int):
    user_id = int(get_jwt_identity())
    row = Download.query.filter_by(download_id=download_id, user_id=user_id).first()
    if not row:
        return jsonify({"error": "download not found"}), 404
    return jsonify(
        {
            "download_id": row.download_id,
            "content_type": row.content_type,
            "file_path": row.file_path,
            "download_url": f"/api/downloads/file/{row.download_id}",
            "timestamp": row.timestamp.isoformat(),
        }
    )


@download_bp.delete("/mine/<int:download_id>")
@jwt_required()
def delete_download(download_id: int):
    user_id = int(get_jwt_identity())
    row = Download.query.filter_by(download_id=download_id, user_id=user_id).first()
    if not row:
        return jsonify({"error": "download not found"}), 404

    file_path = Path(row.file_path)
    if file_path.exists() and file_path.is_file():
        try:
            file_path.unlink()
        except OSError:
            pass

    db.session.delete(row)
    db.session.commit()
    return jsonify({"message": "download deleted", "download_id": download_id})
