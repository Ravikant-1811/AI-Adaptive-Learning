from pathlib import Path
from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models import Download, LearningStyle, ChatHistory
from app.services.adaptive_content_service import generate_learning_asset
from app.services.download_service import create_download_file


download_bp = Blueprint("download", __name__, url_prefix="/api/downloads")


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

    if not str(content).strip():
        content = generate_learning_asset(style_row.learning_style, content_type, topic, base_content)

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
