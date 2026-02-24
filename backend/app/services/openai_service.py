import json
import os
import re
from typing import Any
from pathlib import Path

import requests


OPENAI_CHAT_COMPLETIONS_URL = "https://api.openai.com/v1/chat/completions"
OPENAI_SPEECH_URL = "https://api.openai.com/v1/audio/speech"
OPENAI_IMAGE_URL = "https://api.openai.com/v1/images/generations"
ELEVENLABS_BASE_URL = "https://api.elevenlabs.io/v1/text-to-speech"


def _extract_text(payload: dict[str, Any]) -> str:
    if payload.get("output_text"):
        return str(payload["output_text"]).strip()

    text_parts: list[str] = []
    for item in payload.get("output", []):
        for content in item.get("content", []):
            if content.get("type") in {"output_text", "text"} and content.get("text"):
                text_parts.append(content["text"])
    return "\n".join(text_parts).strip()


def _extract_json(text: str) -> dict[str, Any] | None:
    text = text.strip()
    if not text:
        return None

    # Handle markdown code fences.
    fenced = re.search(r"```(?:json)?\s*(\{[\s\S]*\})\s*```", text)
    if fenced:
        text = fenced.group(1)

    try:
        parsed = json.loads(text)
        return parsed if isinstance(parsed, dict) else None
    except json.JSONDecodeError:
        pass

    # Best-effort extraction of the first JSON object.
    direct = re.search(r"\{[\s\S]*\}", text)
    if not direct:
        return None
    try:
        parsed = json.loads(direct.group(0))
        return parsed if isinstance(parsed, dict) else None
    except json.JSONDecodeError:
        return None


def chatgpt_json(system_prompt: str, user_prompt: str, temperature: float = 0.3) -> dict[str, Any] | None:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()
    if not api_key:
        return None

    try:
        response = requests.post(
            OPENAI_CHAT_COMPLETIONS_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "temperature": temperature,
                "response_format": {"type": "json_object"},
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            },
            timeout=12,
        )
        response.raise_for_status()
        data = response.json()
        content = ((data.get("choices") or [{}])[0].get("message") or {}).get("content", "")
        return _extract_json(content)
    except Exception:
        return None


def chatgpt_text(system_prompt: str, user_prompt: str, temperature: float = 0.4) -> str | None:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()
    if not api_key:
        return None

    try:
        response = requests.post(
            OPENAI_CHAT_COMPLETIONS_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "temperature": temperature,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            },
            timeout=12,
        )
        response.raise_for_status()
        data = response.json()
        text = ((data.get("choices") or [{}])[0].get("message") or {}).get("content", "")
        return text or None
    except Exception:
        return None


def generate_tts_mp3(text: str, output_path: str) -> bool:
    if not text.strip():
        return False

    # Prefer ElevenLabs when key is available.
    eleven_api_key = os.getenv("ELEVENLABS_API_KEY", "").strip()
    eleven_voice_id = os.getenv("ELEVENLABS_VOICE_ID", "EXAVITQu4vr4xnSDxMaL").strip()
    eleven_model_id = os.getenv("ELEVENLABS_MODEL_ID", "eleven_multilingual_v2").strip()
    if eleven_api_key and eleven_voice_id:
        try:
            response = requests.post(
                f"{ELEVENLABS_BASE_URL}/{eleven_voice_id}",
                headers={
                    "xi-api-key": eleven_api_key,
                    "Content-Type": "application/json",
                    "Accept": "audio/mpeg",
                },
                json={
                    "text": text[:3500],
                    "model_id": eleven_model_id,
                    "voice_settings": {
                        "stability": 0.45,
                        "similarity_boost": 0.75,
                    },
                },
                timeout=25,
            )
            response.raise_for_status()
            out = Path(output_path)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(response.content)
            return True
        except Exception:
            # fall back to OpenAI TTS
            pass

    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        return False

    tts_model = os.getenv("OPENAI_TTS_MODEL", "gpt-4o-mini-tts").strip()
    voice = os.getenv("OPENAI_TTS_VOICE", "alloy").strip()

    try:
        response = requests.post(
            OPENAI_SPEECH_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": tts_model,
                "voice": voice,
                "input": text[:4000],
                "format": "mp3",
            },
            timeout=20,
        )
        response.raise_for_status()
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(response.content)
        return True
    except Exception:
        return False


def generate_image_data_url(prompt: str, size: str = "1024x1024") -> str | None:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key or not prompt.strip():
        return None

    image_model = os.getenv("OPENAI_IMAGE_MODEL", "gpt-image-1").strip()
    try:
        response = requests.post(
            OPENAI_IMAGE_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": image_model,
                "prompt": prompt[:3200],
                "size": size,
            },
            timeout=16,
        )
        response.raise_for_status()
        payload = response.json()
        data = (payload.get("data") or [{}])[0]
        b64 = data.get("b64_json")
        if b64:
            return f"data:image/png;base64,{b64}"
        url = data.get("url")
        if url:
            return str(url)
        return None
    except Exception:
        return None
