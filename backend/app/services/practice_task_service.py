from app.services.openai_service import chatgpt_json


DEFAULT_TASKS = [
    {
        "task_name": "Try-catch for divide by zero",
        "description": "Handle ArithmeticException and print a user-friendly message.",
        "starter_code": (
            "public class Main {\n"
            "  public static void main(String[] args) {\n"
            "    try {\n"
            "      int result = 20 / 0;\n"
            "      System.out.println(result);\n"
            "    } catch (ArithmeticException e) {\n"
            "      System.out.println(\"Handled: \" + e.getMessage());\n"
            "    } finally {\n"
            "      System.out.println(\"Complete\");\n"
            "    }\n"
            "  }\n"
            "}"
        ),
    },
    {
        "task_name": "Handle multiple exceptions",
        "description": "Use separate catch blocks for ArithmeticException and NullPointerException.",
        "starter_code": (
            "public class Main {\n"
            "  public static void main(String[] args) {\n"
            "    try {\n"
            "      String value = null;\n"
            "      System.out.println(value.length());\n"
            "    } catch (NullPointerException e) {\n"
            "      System.out.println(\"Null handled\");\n"
            "    } catch (ArithmeticException e) {\n"
            "      System.out.println(\"Math handled\");\n"
            "    }\n"
            "  }\n"
            "}"
        ),
    },
    {
        "task_name": "finally block cleanup",
        "description": "Ensure finally block runs whether exception occurs or not.",
        "starter_code": (
            "public class Main {\n"
            "  public static void main(String[] args) {\n"
            "    try {\n"
            "      System.out.println(\"Run task\");\n"
            "    } finally {\n"
            "      System.out.println(\"Cleanup always runs\");\n"
            "    }\n"
            "  }\n"
            "}"
        ),
    },
]


def _validate_tasks(items: list[dict]) -> list[dict]:
    valid = []
    for item in items:
        task_name = str(item.get("task_name", "")).strip()
        description = str(item.get("description", "")).strip()
        starter_code = str(item.get("starter_code", "")).strip()
        if not task_name or not description or not starter_code:
            continue
        if "class" not in starter_code or "main" not in starter_code:
            continue
        valid.append(
            {
                "task_name": task_name,
                "description": description,
                "starter_code": starter_code,
            }
        )
    return valid


def _is_low_signal_topic(topic: str) -> bool:
    text = (topic or "").strip().lower()
    if not text:
        return True
    low_signal_phrases = {
        "i want learn new things",
        "learn new things",
        "new things",
        "hello",
        "hi",
        "help me",
        "anything",
    }
    if text in low_signal_phrases:
        return True
    return len(text.split()) < 3


def _merge_with_defaults(tasks: list[dict], count: int) -> list[dict]:
    merged: list[dict] = []
    seen = set()
    for item in tasks + DEFAULT_TASKS:
        key = item["task_name"].strip().lower()
        if key in seen:
            continue
        seen.add(key)
        merged.append(item)
        if len(merged) >= count:
            break
    return merged


def generate_practice_tasks_from_topic(topic: str, count: int = 3) -> tuple[list[dict], str]:
    clean_topic = (topic or "").strip()
    safe_count = max(1, min(5, int(count)))
    if not clean_topic or _is_low_signal_topic(clean_topic):
        return DEFAULT_TASKS[:safe_count], "default"

    system_prompt = (
        "You are a Java tutor creating practical exception-handling practice tasks. "
        "Return strict JSON only."
    )
    user_prompt = (
        f"Generate {safe_count} Java coding tasks for this topic: {clean_topic}.\n"
        "Output JSON object:\n"
        "{\n"
        "  \"tasks\": [\n"
        "    {\n"
        "      \"task_name\": \"...\",\n"
        "      \"description\": \"...\",\n"
        "      \"starter_code\": \"...\"\n"
        "    }\n"
        "  ]\n"
        "}\n"
        "Rules: starter_code must be valid Java with class Main and main method."
    )

    payload = chatgpt_json(system_prompt, user_prompt, temperature=0.4)
    if not payload or not isinstance(payload.get("tasks"), list):
        return DEFAULT_TASKS[:safe_count], "default"

    tasks = _validate_tasks(payload["tasks"])
    if len(tasks) < 1:
        return DEFAULT_TASKS[:safe_count], "default"

    return _merge_with_defaults(tasks, safe_count), "ai"
