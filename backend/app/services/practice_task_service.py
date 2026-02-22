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


def generate_practice_tasks_from_topic(topic: str, count: int = 3) -> tuple[list[dict], str]:
    clean_topic = (topic or "").strip()
    if not clean_topic:
        return DEFAULT_TASKS, "default"

    system_prompt = (
        "You are a Java tutor creating practical exception-handling practice tasks. "
        "Return strict JSON only."
    )
    user_prompt = (
        f"Generate {count} Java coding tasks for this topic: {clean_topic}.\n"
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
        return DEFAULT_TASKS, "default"

    tasks = _validate_tasks(payload["tasks"])
    if len(tasks) < 1:
        return DEFAULT_TASKS, "default"

    return tasks[:count], "ai"
