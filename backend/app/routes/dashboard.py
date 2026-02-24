from collections import Counter
from datetime import datetime, timedelta

from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.models import ChatHistory, Download, PracticeActivity


dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/api/dashboard")


def _date_key(dt):
    return dt.strftime("%Y-%m-%d")


def _build_daily_series(items, date_attr: str, days: int = 7):
    today = datetime.utcnow().date()
    labels = [(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(days - 1, -1, -1)]
    count_map = {k: 0 for k in labels}
    for item in items:
        value = getattr(item, date_attr, None)
        if not value:
            continue
        key = _date_key(value)
        if key in count_map:
            count_map[key] += 1
    return [{"date": day, "count": count_map[day]} for day in labels]


@dashboard_bp.get("/insights")
@jwt_required()
def insights():
    user_id = int(get_jwt_identity())
    chats = (
        ChatHistory.query.filter_by(user_id=user_id)
        .order_by(ChatHistory.timestamp.desc())
        .limit(120)
        .all()
    )
    downloads = (
        Download.query.filter_by(user_id=user_id)
        .order_by(Download.timestamp.desc())
        .limit(120)
        .all()
    )
    practices = (
        PracticeActivity.query.filter_by(user_id=user_id)
        .order_by(PracticeActivity.updated_at.desc())
        .limit(120)
        .all()
    )

    completed = [p for p in practices if (p.status or "").lower() == "completed"]
    total_time = sum((p.time_spent or 0) for p in practices)
    mastery_score = min(100, int(len(completed) * 12 + min(total_time / 45, 45)))

    # simple recommendation from most frequent recent topic keywords
    topic_counter = Counter()
    for row in chats[:25]:
        for token in row.question.lower().split():
            clean = "".join(ch for ch in token if ch.isalnum())
            if len(clean) < 4:
                continue
            if clean in {"explain", "about", "what", "does", "java", "with", "from", "into"}:
                continue
            topic_counter[clean] += 1
    top = topic_counter.most_common(1)
    recommended = f"Advanced {top[0][0].capitalize()} in Java" if top else "Object-oriented programming fundamentals"

    # streak = consecutive days with any activity ending today
    activity_days = set()
    for row in chats:
        activity_days.add(_date_key(row.timestamp))
    for row in downloads:
        activity_days.add(_date_key(row.timestamp))
    for row in practices:
        activity_days.add(_date_key(row.updated_at))
    streak = 0
    cursor = datetime.utcnow().date()
    while cursor.strftime("%Y-%m-%d") in activity_days:
        streak += 1
        cursor -= timedelta(days=1)

    return jsonify(
        {
            "mastery_score": mastery_score,
            "streak_days": streak,
            "recommended_topic": recommended,
            "daily_chat": _build_daily_series(chats, "timestamp", days=7),
            "daily_practice": _build_daily_series(practices, "updated_at", days=7),
            "daily_downloads": _build_daily_series(downloads, "timestamp", days=7),
        }
    )
