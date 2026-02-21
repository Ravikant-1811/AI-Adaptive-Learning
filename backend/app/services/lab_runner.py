import os
import requests


LANGUAGE_JAVA = 62


def run_java_code(source_code: str) -> dict:
    base_url = os.getenv("JUDGE0_BASE_URL", "").strip().rstrip("/")
    api_key = os.getenv("JUDGE0_API_KEY", "").strip()
    api_host = os.getenv("JUDGE0_API_HOST", "").strip()

    if not base_url or not api_key or not api_host:
        # Offline fallback to keep the project runnable without API credentials.
        if "class" in source_code and "main" in source_code:
            return {
                "status": "success",
                "stdout": "Simulated execution success. Configure Judge0 API for real compilation.",
                "stderr": "",
            }
        return {
            "status": "error",
            "stdout": "",
            "stderr": "Simulated compile error: class/main method not found.",
        }

    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": api_host,
        "Content-Type": "application/json",
    }

    submit_resp = requests.post(
        f"{base_url}/submissions?base64_encoded=false&wait=true",
        headers=headers,
        json={
            "language_id": LANGUAGE_JAVA,
            "source_code": source_code,
        },
        timeout=40,
    )
    submit_resp.raise_for_status()
    payload = submit_resp.json()

    return {
        "status": "success" if (payload.get("status") or {}).get("id") == 3 else "error",
        "stdout": payload.get("stdout") or "",
        "stderr": payload.get("stderr") or payload.get("compile_output") or "",
        "judge0_status": (payload.get("status") or {}).get("description", "unknown"),
    }
