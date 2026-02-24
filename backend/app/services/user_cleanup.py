from pathlib import Path

from app.extensions import db
from app.models import ChatFeedback, ChatHistory, Download, LearningStyle, PasswordResetToken, PracticeActivity, User


def delete_user_with_related_data(user_id: int) -> bool:
    user = User.query.get(user_id)
    if not user:
        return False

    download_rows = Download.query.filter_by(user_id=user_id).all()
    for row in download_rows:
        p = Path(row.file_path)
        if p.exists() and p.is_file():
            try:
                p.unlink()
            except OSError:
                pass

    ChatHistory.query.filter_by(user_id=user_id).delete()
    ChatFeedback.query.filter_by(user_id=user_id).delete()
    PracticeActivity.query.filter_by(user_id=user_id).delete()
    Download.query.filter_by(user_id=user_id).delete()
    LearningStyle.query.filter_by(user_id=user_id).delete()
    PasswordResetToken.query.filter_by(user_id=user_id).delete()
    db.session.delete(user)
    db.session.commit()
    return True
