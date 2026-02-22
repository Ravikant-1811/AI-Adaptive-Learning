from app.services.openai_service import chatgpt_text


def _fallback_response(question: str, style: str) -> str:
    topic = question.strip().rstrip("?")
    if style == "visual":
        return (
            f"Visual Learning Plan for: {topic}\n\n"
            "1. Big picture map\n"
            "2. Process flow and error path\n"
            "3. One solved visual example\n"
            "4. One-page visual revision"
        )
    if style == "auditory":
        return (
            f"Auditory Learning Script for: {topic}\n\n"
            "- Listen in short chunks.\n"
            "- Repeat key ideas aloud.\n"
            "- Record your own summary."
        )
    return (
        f"Kinesthetic Practice Path for: {topic}\n\n"
        "Step 1: Write code skeleton.\n"
        "Step 2: Add try/catch/finally.\n"
        "Step 3: Run and test failure cases.\n"
        "Step 4: Refactor and re-run."
    )


def _generate_chatgpt_explanation(question: str, style: str) -> str | None:
    style_prompt = {
        "visual": "Give a visual-first explanation with flow structure, diagram-like bullets, and concise steps.",
        "auditory": "Give a spoken-style explanation in simple conversational language, clear and concise.",
        "kinesthetic": "Give a hands-on explanation with a practical coding exercise and step-by-step task flow.",
    }
    system_prompt = (
        "You are an adaptive tutor. Keep responses clear, practical, and beginner friendly. "
        "Return plain text only."
    )
    user_prompt = f"Question: {question}\nLearning style: {style}\nInstruction: {style_prompt.get(style, '')}"
    return chatgpt_text(system_prompt, user_prompt, temperature=0.5)


def generate_adaptive_response(question: str, style: str) -> dict:
    topic = question.strip().rstrip("?")
    ai_text = _generate_chatgpt_explanation(question, style)
    text = ai_text or _fallback_response(question, style)
    ai_used = bool(ai_text)

    if style == "visual":
        return {
            "response_type": "visual",
            "ai_used": ai_used,
            "text": text,
            "assets": {
                "diagram": "Input -> Try Block -> Exception Raised? -> Catch -> Finally -> Continue",
                "video_url": "https://www.youtube.com/watch?v=1XAfapkBQjk",
                "gif_url": "https://media.giphy.com/media/26ufdipQqU2lhNA4g/giphy.gif",
                "suggested_downloads": ["pdf", "video"],
            },
        }

    if style == "auditory":
        return {
            "response_type": "auditory",
            "ai_used": ai_used,
            "text": text,
            "assets": {
                "audio_script": f"Audio-style explanation for {topic}. {text}",
                "audio_url": "https://www2.cs.uic.edu/~i101/SoundFiles/BabyElephantWalk60.wav",
                "suggested_downloads": ["audio"],
            },
        }

    starter_code = (
        "public class ExceptionDemo {\n"
        "  public static void main(String[] args) {\n"
        "    try {\n"
        "      int[] values = {1, 2, 3};\n"
        "      int result = values[4];\n"
        "      System.out.println(result);\n"
        "    } catch (ArrayIndexOutOfBoundsException e) {\n"
        "      System.out.println(\"Handled: \" + e.getMessage());\n"
        "    } finally {\n"
        "      System.out.println(\"Cleanup complete\");\n"
        "    }\n"
        "  }\n"
        "}"
    )
    return {
        "response_type": "kinesthetic",
        "ai_used": ai_used,
        "text": text,
        "assets": {
            "starter_code": starter_code,
            "task_sheet": "Implement try-catch-finally and test two failure cases.",
            "suggested_downloads": ["task_sheet", "solution"],
        },
    }
