from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models import PracticeActivity, LearningStyle, ChatHistory
from app.services.lab_runner import run_java_code
from app.services.practice_task_service import generate_practice_tasks_from_topic, get_topic_catalog


practice_bp = Blueprint("practice", __name__, url_prefix="/api/practice")


def _ensure_kinesthetic(user_id: int):
    style_row = LearningStyle.query.get(user_id)
    if not style_row:
        return jsonify({"error": "learning style not set"}), 400
    if style_row.learning_style != "kinesthetic":
        return jsonify({"error": "practice lab is available only for kinesthetic users"}), 403
    return None


@practice_bp.get("/tasks")
@jwt_required()
def tasks():
    user_id = int(get_jwt_identity())
    guard = _ensure_kinesthetic(user_id)
    if guard:
        return guard

    requested_topic = request.args.get("topic", "").strip()
    if requested_topic:
        topic = requested_topic
    else:
        latest_chat = (
            ChatHistory.query.filter_by(user_id=user_id)
            .order_by(ChatHistory.timestamp.desc())
            .first()
        )
        topic = latest_chat.question if latest_chat else "Java exception handling"
    generated_tasks, source = generate_practice_tasks_from_topic(topic, count=3)
    return jsonify({"tasks": generated_tasks, "topic": topic, "source": source})


@practice_bp.get("/topics")
@jwt_required()
def topics():
    user_id = int(get_jwt_identity())
    guard = _ensure_kinesthetic(user_id)
    if guard:
        return guard
    return jsonify({"topics": get_topic_catalog()})


@practice_bp.post("/run")
@jwt_required()
def run_code():
    user_id = int(get_jwt_identity())
    guard = _ensure_kinesthetic(user_id)
    if guard:
        return guard

    source_code = (request.get_json() or {}).get("source_code", "")
    if not source_code.strip():
        return jsonify({"error": "source_code is required"}), 400

    result = run_java_code(source_code)
    return jsonify(result)


@practice_bp.post("/submit")
@jwt_required()
def submit_activity():
    user_id = int(get_jwt_identity())
    guard = _ensure_kinesthetic(user_id)
    if guard:
        return guard

    data = request.get_json() or {}
    task_name = data.get("task_name", "").strip()
    status = data.get("status", "completed").strip() or "completed"
    code_submitted = data.get("code_submitted", "")
    try:
        time_spent = max(0, int(data.get("time_spent", 0)))
    except (TypeError, ValueError):
        return jsonify({"error": "time_spent must be a valid integer"}), 400

    if not task_name:
        return jsonify({"error": "task_name is required"}), 400

    activity = PracticeActivity(
        user_id=user_id,
        task_name=task_name,
        status=status,
        code_submitted=code_submitted,
        time_spent=time_spent,
    )
    db.session.add(activity)
    db.session.commit()

    return jsonify({"message": "practice activity saved", "activity_id": activity.activity_id})


@practice_bp.get("/mine")
@jwt_required()
def my_activities():
    user_id = int(get_jwt_identity())
    guard = _ensure_kinesthetic(user_id)
    if guard:
        return guard

    rows = (
        PracticeActivity.query.filter_by(user_id=user_id)
        .order_by(PracticeActivity.updated_at.desc())
        .limit(30)
        .all()
    )
    return jsonify(
        [
            {
                "activity_id": r.activity_id,
                "task_name": r.task_name,
                "status": r.status,
                "time_spent": r.time_spent,
                "updated_at": r.updated_at.isoformat(),
            }
            for r in rows
        ]
    )


@practice_bp.get("/mine/<int:activity_id>")
@jwt_required()
def get_activity(activity_id: int):
    user_id = int(get_jwt_identity())
    guard = _ensure_kinesthetic(user_id)
    if guard:
        return guard

    row = PracticeActivity.query.filter_by(activity_id=activity_id, user_id=user_id).first()
    if not row:
        return jsonify({"error": "activity not found"}), 404

    return jsonify(
        {
            "activity_id": row.activity_id,
            "task_name": row.task_name,
            "status": row.status,
            "code_submitted": row.code_submitted or "",
            "time_spent": row.time_spent,
            "created_at": row.created_at.isoformat(),
            "updated_at": row.updated_at.isoformat(),
        }
    )


@practice_bp.put("/mine/<int:activity_id>")
@jwt_required()
def update_activity(activity_id: int):
    user_id = int(get_jwt_identity())
    guard = _ensure_kinesthetic(user_id)
    if guard:
        return guard

    row = PracticeActivity.query.filter_by(activity_id=activity_id, user_id=user_id).first()
    if not row:
        return jsonify({"error": "activity not found"}), 404

    data = request.get_json() or {}
    if "task_name" in data:
        task_name = str(data.get("task_name", "")).strip()
        if not task_name:
            return jsonify({"error": "task_name cannot be empty"}), 400
        row.task_name = task_name

    if "status" in data:
        status = str(data.get("status", "")).strip()
        if not status:
            return jsonify({"error": "status cannot be empty"}), 400
        row.status = status

    if "code_submitted" in data:
        row.code_submitted = str(data.get("code_submitted", ""))

    if "time_spent" in data:
        try:
            row.time_spent = max(0, int(data.get("time_spent", 0)))
        except (TypeError, ValueError):
            return jsonify({"error": "time_spent must be a valid integer"}), 400

    db.session.commit()
    return jsonify({"message": "activity updated", "activity_id": row.activity_id})


@practice_bp.delete("/mine/<int:activity_id>")
@jwt_required()
def delete_activity(activity_id: int):
    user_id = int(get_jwt_identity())
    guard = _ensure_kinesthetic(user_id)
    if guard:
        return guard

    row = PracticeActivity.query.filter_by(activity_id=activity_id, user_id=user_id).first()
    if not row:
        return jsonify({"error": "activity not found"}), 404

    db.session.delete(row)
    db.session.commit()
    return jsonify({"message": "activity deleted", "activity_id": activity_id})
