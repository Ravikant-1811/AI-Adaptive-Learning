from pathlib import Path
from datetime import datetime


DOWNLOAD_DIR = Path(__file__).resolve().parents[2] / "downloads"
DOWNLOAD_DIR.mkdir(exist_ok=True)


EXTENSIONS = {
    "pdf": "txt",
    "video": "txt",
    "audio": "txt",
    "task_sheet": "txt",
    "solution": "txt",
}


def create_download_file(user_id: int, content_type: str, payload: str) -> str:
    ts = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    ext = EXTENSIONS.get(content_type, "txt")
    file_path = DOWNLOAD_DIR / f"u{user_id}_{content_type}_{ts}.{ext}"
    file_path.write_text(payload, encoding="utf-8")
    return str(file_path)
