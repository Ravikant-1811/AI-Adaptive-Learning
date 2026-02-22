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

TOPIC_TASK_BANK = {
    "Java Exception Basics": DEFAULT_TASKS,
    "File Handling Exceptions": [
        {
            "task_name": "Read file with try-catch",
            "description": "Read a text file and handle FileNotFoundException gracefully.",
            "starter_code": (
                "import java.io.*;\n"
                "public class Main {\n"
                "  public static void main(String[] args) {\n"
                "    try {\n"
                "      BufferedReader br = new BufferedReader(new FileReader(\"input.txt\"));\n"
                "      System.out.println(br.readLine());\n"
                "      br.close();\n"
                "    } catch (FileNotFoundException e) {\n"
                "      System.out.println(\"File missing: \" + e.getMessage());\n"
                "    } catch (IOException e) {\n"
                "      System.out.println(\"IO error: \" + e.getMessage());\n"
                "    }\n"
                "  }\n"
                "}"
            ),
        },
        {
            "task_name": "Write file safely",
            "description": "Write text to file and handle IOException with proper cleanup.",
            "starter_code": (
                "import java.io.*;\n"
                "public class Main {\n"
                "  public static void main(String[] args) {\n"
                "    BufferedWriter bw = null;\n"
                "    try {\n"
                "      bw = new BufferedWriter(new FileWriter(\"out.txt\"));\n"
                "      bw.write(\"Hello\");\n"
                "    } catch (IOException e) {\n"
                "      System.out.println(\"Write failed: \" + e.getMessage());\n"
                "    } finally {\n"
                "      try { if (bw != null) bw.close(); } catch (IOException ignored) {}\n"
                "    }\n"
                "  }\n"
                "}"
            ),
        },
        {
            "task_name": "Parse file numbers",
            "description": "Read a file line and handle NumberFormatException while parsing integer.",
            "starter_code": (
                "import java.io.*;\n"
                "public class Main {\n"
                "  public static void main(String[] args) {\n"
                "    try {\n"
                "      String text = \"abc\";\n"
                "      int n = Integer.parseInt(text);\n"
                "      System.out.println(n);\n"
                "    } catch (NumberFormatException e) {\n"
                "      System.out.println(\"Invalid number: \" + e.getMessage());\n"
                "    }\n"
                "  }\n"
                "}"
            ),
        },
    ],
    "Collections and Null Safety": [
        {
            "task_name": "Null list handling",
            "description": "Handle NullPointerException while reading from a null list reference.",
            "starter_code": (
                "import java.util.*;\n"
                "public class Main {\n"
                "  public static void main(String[] args) {\n"
                "    List<String> names = null;\n"
                "    try {\n"
                "      System.out.println(names.get(0));\n"
                "    } catch (NullPointerException e) {\n"
                "      System.out.println(\"Null list handled\");\n"
                "    }\n"
                "  }\n"
                "}"
            ),
        },
        {
            "task_name": "Index bounds handling",
            "description": "Catch IndexOutOfBoundsException when list index is invalid.",
            "starter_code": (
                "import java.util.*;\n"
                "public class Main {\n"
                "  public static void main(String[] args) {\n"
                "    List<Integer> nums = Arrays.asList(1, 2, 3);\n"
                "    try {\n"
                "      System.out.println(nums.get(10));\n"
                "    } catch (IndexOutOfBoundsException e) {\n"
                "      System.out.println(\"Invalid index\");\n"
                "    }\n"
                "  }\n"
                "}"
            ),
        },
        {
            "task_name": "Multiple catch with collections",
            "description": "Use multiple catch blocks for NumberFormatException and NullPointerException.",
            "starter_code": (
                "public class Main {\n"
                "  public static void main(String[] args) {\n"
                "    String value = null;\n"
                "    try {\n"
                "      int n = Integer.parseInt(value);\n"
                "      System.out.println(n);\n"
                "    } catch (NumberFormatException e) {\n"
                "      System.out.println(\"Number error\");\n"
                "    } catch (NullPointerException e) {\n"
                "      System.out.println(\"Null value\");\n"
                "    }\n"
                "  }\n"
                "}"
            ),
        },
    ],
    "Custom Exceptions": [
        {
            "task_name": "Throw custom exception",
            "description": "Create and throw a custom exception for invalid age input.",
            "starter_code": (
                "class InvalidAgeException extends Exception {\n"
                "  InvalidAgeException(String msg) { super(msg); }\n"
                "}\n"
                "public class Main {\n"
                "  static void validate(int age) throws InvalidAgeException {\n"
                "    if (age < 18) throw new InvalidAgeException(\"Age must be 18+\");\n"
                "  }\n"
                "  public static void main(String[] args) {\n"
                "    try { validate(15); } catch (InvalidAgeException e) { System.out.println(e.getMessage()); }\n"
                "  }\n"
                "}"
            ),
        },
        {
            "task_name": "Rethrow checked exception",
            "description": "Catch IOException and rethrow it with additional context.",
            "starter_code": (
                "import java.io.*;\n"
                "public class Main {\n"
                "  static void load() throws IOException {\n"
                "    try { throw new IOException(\"Disk read failed\"); }\n"
                "    catch (IOException e) { throw new IOException(\"Load failed: \" + e.getMessage()); }\n"
                "  }\n"
                "  public static void main(String[] args) {\n"
                "    try { load(); } catch (IOException e) { System.out.println(e.getMessage()); }\n"
                "  }\n"
                "}"
            ),
        },
        {
            "task_name": "finally with custom flow",
            "description": "Use finally to ensure cleanup after custom exception path.",
            "starter_code": (
                "class AppException extends Exception { AppException(String m) { super(m); } }\n"
                "public class Main {\n"
                "  public static void main(String[] args) {\n"
                "    try {\n"
                "      throw new AppException(\"App flow broke\");\n"
                "    } catch (AppException e) {\n"
                "      System.out.println(e.getMessage());\n"
                "    } finally {\n"
                "      System.out.println(\"Cleanup done\");\n"
                "    }\n"
                "  }\n"
                "}"
            ),
        },
    ],
}


def _normalize_topic(topic: str) -> str:
    return " ".join((topic or "").strip().lower().split())


def _topic_tasks_from_bank(topic: str, count: int) -> list[dict] | None:
    query = _normalize_topic(topic)
    if not query:
        return None
    for bank_topic, tasks in TOPIC_TASK_BANK.items():
        bank_norm = _normalize_topic(bank_topic)
        if query in bank_norm or bank_norm in query:
            return tasks[:count]
    keyword_map = {
        "file": "File Handling Exceptions",
        "io": "File Handling Exceptions",
        "null": "Collections and Null Safety",
        "collection": "Collections and Null Safety",
        "custom": "Custom Exceptions",
        "user-defined": "Custom Exceptions",
        "exception": "Java Exception Basics",
    }
    for keyword, mapped_topic in keyword_map.items():
        if keyword in query:
            return TOPIC_TASK_BANK[mapped_topic][:count]
    return None


def get_topic_catalog() -> list[dict]:
    catalog: list[dict] = []
    for topic, tasks in TOPIC_TASK_BANK.items():
        catalog.append(
            {
                "topic": topic,
                "tasks": [
                    {"task_name": task["task_name"], "description": task["description"]}
                    for task in tasks
                ],
            }
        )
    return catalog


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
    bank_tasks = _topic_tasks_from_bank(clean_topic, safe_count)
    if bank_tasks:
        return bank_tasks, "catalog"
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
