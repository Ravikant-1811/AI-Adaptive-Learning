from pathlib import Path
from datetime import datetime
import math
import struct
import wave
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


def _write_fallback_wav(path: Path, duration_seconds: float = 1.2, sample_rate: int = 16000) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    n_frames = int(duration_seconds * sample_rate)
    frequency = 440.0
    amplitude = 9000

    with wave.open(str(path), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        frames = bytearray()
        for i in range(n_frames):
            sample = int(amplitude * math.sin(2 * math.pi * frequency * (i / sample_rate)))
            frames.extend(struct.pack("<h", sample))
        wav_file.writeframes(bytes(frames))


def create_download_file(user_id: int, content_type: str, payload: str) -> str:
    ts = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    ext = EXTENSIONS.get(content_type, "txt")
    file_path = DOWNLOAD_DIR / f"u{user_id}_{content_type}_{ts}.{ext}"
    if content_type == "audio":
        if not generate_tts_mp3(payload, str(file_path)):
            # Fallback to a valid playable WAV file so UI audio player still works.
            wav_path = DOWNLOAD_DIR / f"u{user_id}_{content_type}_{ts}.wav"
            try:
                _write_fallback_wav(wav_path)
                return str(wav_path)
            except Exception:
                # Last fallback text payload when audio file generation is unavailable.
                file_path = DOWNLOAD_DIR / f"u{user_id}_{content_type}_{ts}.txt"
                file_path.write_text(payload, encoding="utf-8")
        return str(file_path)

    file_path.write_text(payload, encoding="utf-8")
    return str(file_path)
