from pathlib import Path
from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models import Download, LearningStyle
from app.services.download_service import create_download_file


download_bp = Blueprint("download", __name__, url_prefix="/api/downloads")


@download_bp.post("/")
@jwt_required()
def create_download():
    user_id = int(get_jwt_identity())
    payload = request.get_json() or {}
    content_type = payload.get("content_type", "").strip()
    content = payload.get("content", "Sample generated content")

    style_row = LearningStyle.query.get(user_id)
    if not style_row:
        return jsonify({"error": "learning style not set"}), 400

    allowed_by_style = {
        "visual": {"pdf", "video"},
        "auditory": {"audio"},
        "kinesthetic": {"task_sheet", "solution"},
    }

    if content_type not in allowed_by_style[style_row.learning_style]:
        return jsonify({"error": f"{content_type} is not allowed for {style_row.learning_style}"}), 400

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
