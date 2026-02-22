import os
import requests


LANGUAGE_JAVA = 62


def _simulate_java_result(source_code: str, reason: str) -> dict:
    normalized = source_code or ""
    has_class_main = "class" in normalized and "main" in normalized
    has_try = "try" in normalized
    has_catch = "catch" in normalized
    has_finally = "finally" in normalized

    if not has_class_main:
        return {
            "status": "error",
            "stdout": "",
            "stderr": "Simulated compile error: class/main method not found.",
            "judge0_status": "simulation",
            "runner": "simulated",
            "note": reason,
        }

    hints = []
    if has_try and has_catch:
        hints.append("Detected try-catch block.")
    if has_finally:
        hints.append("Detected finally block.")
    if "/ 0" in normalized or "throw new" in normalized:
        hints.append("Possible exception path identified.")

    stdout = "Simulated execution success."
    if hints:
        stdout = f"{stdout} " + " ".join(hints)

    return {
        "status": "success",
        "stdout": stdout,
        "stderr": "",
        "judge0_status": "simulation",
        "runner": "simulated",
        "note": reason,
    }


def _valid_judge0_creds(base_url: str, api_key: str, api_host: str) -> bool:
    if not base_url or not api_key or not api_host:
        return False
    placeholder_tokens = {"your-rapidapi-key", "changeme", "none", "null"}
    return api_key.strip().lower() not in placeholder_tokens


def run_java_code(source_code: str) -> dict:
    base_url = os.getenv("JUDGE0_BASE_URL", "").strip().rstrip("/")
    api_key = os.getenv("JUDGE0_API_KEY", "").strip()
    api_host = os.getenv("JUDGE0_API_HOST", "").strip()

    if not _valid_judge0_creds(base_url, api_key, api_host):
        return _simulate_java_result(
            source_code,
            "Judge0 credentials missing or placeholder. Add valid credentials for real compilation.",
        )

    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": api_host,
        "Content-Type": "application/json",
    }

    try:
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
            "runner": "judge0",
            "note": "",
        }
    except requests.HTTPError as exc:
        status = exc.response.status_code if exc.response is not None else "unknown"
        return _simulate_java_result(
            source_code,
            f"Judge0 HTTP error ({status}). Switched to simulated execution.",
        )
    except requests.RequestException:
        return _simulate_java_result(
            source_code,
            "Judge0 network error. Switched to simulated execution.",
        )
