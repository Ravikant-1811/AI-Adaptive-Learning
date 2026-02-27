from app.services.openai_service import chatgpt_text


def generate_learning_asset(style: str, content_type: str, topic: str, base_content: str = "") -> str:
    topic_clean = (topic or "general programming concept").strip()
    base = (base_content or "").strip()

    style_instruction = {
        "visual": "Create visually structured notes with clear headings, bullets, and a flow sequence.",
        "auditory": "Create a spoken-style script with short sentences and natural narration pacing.",
        "kinesthetic": "Create an action-oriented task sheet with steps, checkpoints, and expected outcomes.",
    }.get(style, "Create clear learning content.")

    type_instruction = {
        "pdf": "Write concise notes suitable for export as PDF.",
        "video": "Write storyboard-style frames for a short explainer video.",
        "audio": "Write an audio narration script.",
        "task_sheet": "Write a practical coding task sheet.",
        "solution": "Write a complete worked solution with explanation.",
    }.get(content_type, "Write useful learning content.")

    system_prompt = (
        "You generate educational assets. Output plain text only, no markdown tables, no code fences."
    )
    user_prompt = (
        f"Topic: {topic_clean}\n"
        f"Learning style: {style}\n"
        f"Requested asset: {content_type}\n"
        f"Instructions: {style_instruction} {type_instruction}\n"
        f"Optional context: {base[:2500]}"
    )

    ai_text = chatgpt_text(system_prompt, user_prompt, temperature=0.5)
    if ai_text:
        return ai_text

    fallback = [
        f"Topic: {topic_clean}",
        f"Learning style: {style}",
        f"Asset type: {content_type}",
        "",
        "This is fallback generated content because AI output was unavailable.",
    ]
    if base:
        fallback.extend(["", "Reference content:", base[:3000]])
    return "\n".join(fallback)


def generate_openai_solution(topic: str, base_content: str = "") -> str:
    topic_clean = (topic or "java practice problem").strip()
    context = (base_content or "").strip()

    system_prompt = (
        "You are a senior Java tutor. Generate a worked solution in plain text only. "
        "No markdown tables and no code fences. Keep it practical and executable."
    )
    user_prompt = (
        f"Topic: {topic_clean}\n"
        "Create a complete solved answer with these sections in order:\n"
        "1) Final Java Code\n"
        "2) Explanation (step-by-step)\n"
        "3) Expected Output\n"
        "4) Common Mistakes\n"
        "5) Quick Improvement Tips\n\n"
        f"Reference context from user/workspace: {context[:2800]}"
    )

    ai_text = chatgpt_text(system_prompt, user_prompt, temperature=0.35)
    if ai_text:
        return ai_text

    fallback = [
        f"Topic: {topic_clean}",
        "Document Type: WORKED SOLUTION",
        "",
        "Final Java Code:",
        "public class Main {",
        "  public static void main(String[] args) {",
        "    try {",
        "      // TODO: implement logic",
        "    } catch (Exception e) {",
        "      System.out.println(\"Handled: \" + e.getMessage());",
        "    } finally {",
        "      System.out.println(\"Done\");",
        "    }",
        "  }",
        "}",
        "",
        "Explanation (step-by-step):",
        "- Build core logic in try block",
        "- Catch specific exceptions first",
        "- Use finally for cleanup",
        "",
        "Expected Output:",
        "- Program runs and prints handled error or result",
        "",
        "Common Mistakes:",
        "- Catching generic Exception too early",
        "- Missing finally cleanup",
    ]
    if context:
        fallback.extend(["", "Reference Context:", context[:1500]])
    return "\n".join(fallback)
