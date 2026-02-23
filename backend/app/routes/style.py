from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models import LearningStyle
from app.services.style_engine import QUESTIONS, evaluate_style, generate_interest_based_questions


style_bp = Blueprint("style", __name__, url_prefix="/api/style")


@style_bp.get("/questions")
@jwt_required()
def questions():
    return jsonify({"questions": QUESTIONS})


@style_bp.post("/generate-questions")
@jwt_required()
def generate_questions():
    payload = request.get_json() or {}
    interests = str(payload.get("interests", "")).strip()
    question_count = int(payload.get("question_count", 20))
    questions, source = generate_interest_based_questions(interests, question_count)
    return jsonify({"questions": questions, "source": source})


@style_bp.post("/select")
@jwt_required()
def select_style():
    user_id = int(get_jwt_identity())
    style = (request.get_json() or {}).get("learning_style", "").strip().lower()
    if style not in {"visual", "auditory", "kinesthetic"}:
        return jsonify({"error": "invalid learning style"}), 400

    score_map = {
        "visual": {"visual_score": 20, "auditory_score": 0, "kinesthetic_score": 0},
        "auditory": {"visual_score": 0, "auditory_score": 20, "kinesthetic_score": 0},
        "kinesthetic": {"visual_score": 0, "auditory_score": 0, "kinesthetic_score": 20},
    }

    record = LearningStyle.query.get(user_id)
    if not record:
        record = LearningStyle(user_id=user_id, learning_style=style, **score_map[style])
        db.session.add(record)
    else:
        record.learning_style = style
        record.visual_score = score_map[style]["visual_score"]
        record.auditory_score = score_map[style]["auditory_score"]
        record.kinesthetic_score = score_map[style]["kinesthetic_score"]

    db.session.commit()
    return jsonify({"message": "learning style saved", "learning_style": style})


@style_bp.post("/submit-test")
@jwt_required()
def submit_test():
    user_id = int(get_jwt_identity())
    answers = (request.get_json() or {}).get("answers", [])

    if not isinstance(answers, list) or not answers:
        return jsonify({"error": "answers list is required"}), 400

    if len(answers) < 10 or len(answers) > 30:
        return jsonify({"error": "answers must be between 10 and 30"}), 400

    if not all(a in {"visual", "auditory", "kinesthetic"} for a in answers):
        return jsonify({"error": "invalid answer value"}), 400

    result = evaluate_style(answers)

    record = LearningStyle.query.get(user_id)
    if not record:
        record = LearningStyle(user_id=user_id, **result)
        db.session.add(record)
    else:
        record.learning_style = result["learning_style"]
        record.visual_score = result["visual_score"]
        record.auditory_score = result["auditory_score"]
        record.kinesthetic_score = result["kinesthetic_score"]

    db.session.commit()
    return jsonify(result)


@style_bp.get("/mine")
@jwt_required()
def my_style():
    user_id = int(get_jwt_identity())
    record = LearningStyle.query.get(user_id)
    if not record:
        return jsonify({"learning_style": None})

    return jsonify(
        {
            "learning_style": record.learning_style,
            "visual_score": record.visual_score,
            "auditory_score": record.auditory_score,
            "kinesthetic_score": record.kinesthetic_score,
        }
    )


@style_bp.delete("/mine")
@jwt_required()
def clear_style():
    user_id = int(get_jwt_identity())
    record = LearningStyle.query.get(user_id)
    if not record:
        return jsonify({"message": "learning style already empty"})
    db.session.delete(record)
    db.session.commit()
    return jsonify({"message": "learning style removed"})
