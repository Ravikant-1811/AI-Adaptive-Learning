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
