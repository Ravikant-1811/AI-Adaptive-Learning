from pathlib import Path
from datetime import datetime
from app.services.openai_service import generate_tts_mp3


DOWNLOAD_DIR = Path(__file__).resolve().parents[2] / "downloads"
DOWNLOAD_DIR.mkdir(exist_ok=True)


EXTENSIONS = {
    "pdf": "txt",
    "video": "txt",
    "audio": "mp3",
    "task_sheet": "txt",
    "solution": "txt",
}


def create_download_file(user_id: int, content_type: str, payload: str) -> str:
    ts = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    ext = EXTENSIONS.get(content_type, "txt")
    file_path = DOWNLOAD_DIR / f"u{user_id}_{content_type}_{ts}.{ext}"
    if content_type == "audio":
        if not generate_tts_mp3(payload, str(file_path)):
            # Fallback text payload when TTS is unavailable.
            file_path = DOWNLOAD_DIR / f"u{user_id}_{content_type}_{ts}.txt"
            file_path.write_text(payload, encoding="utf-8")
        return str(file_path)

    file_path.write_text(payload, encoding="utf-8")
    return str(file_path)
