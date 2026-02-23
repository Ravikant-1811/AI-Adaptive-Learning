import random
import re
from urllib.parse import quote_plus

from app.services.openai_service import chatgpt_text
from urllib.parse import quote


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


def _topic_keywords(topic: str) -> list[str]:
    words = re.findall(r"[A-Za-z][A-Za-z0-9+#-]{2,}", topic)
    filtered = [w for w in words if w.lower() not in {"about", "explain", "learn", "with", "from", "that", "this"}]
    seen = set()
    result = []
    for word in filtered:
        low = word.lower()
        if low in seen:
            continue
        seen.add(low)
        result.append(word.capitalize())
        if len(result) == 5:
            break
    if not result:
        return ["Concept", "Flow", "Example", "Errors", "Practice"]
    return result


def _safe_label(text: str, max_len: int = 28) -> str:
    return (text or "Concept").replace("<", "").replace(">", "").strip()[:max_len]


def _youtube_search_url(topic: str) -> str:
    query = f"{topic} tutorial for beginners"
    return f"https://www.youtube.com/results?search_query={quote_plus(query)}"


def _generate_prompt_suggestions(topic: str, style: str) -> list[str]:
    base_topic = topic.strip() or "Java exception handling"
    system_prompt = (
        "You create short learning prompts. Return exactly 6 lines. "
        "Each line must be one user question. No numbering, no bullets, plain text."
    )
    user_prompt = (
        f"Learning style: {style}\n"
        f"Topic: {base_topic}\n"
        "Generate diverse follow-up questions from beginner to practical level."
    )
    raw = chatgpt_text(system_prompt, user_prompt, temperature=0.8)
    if raw:
        rows = [r.strip(" -\t\r") for r in raw.splitlines() if r.strip()]
        rows = [r for r in rows if len(r) > 5]
        deduped = []
        seen = set()
        for row in rows:
            key = row.lower()
            if key in seen:
                continue
            seen.add(key)
            deduped.append(row)
            if len(deduped) == 6:
                break
        if len(deduped) >= 4:
            return deduped

    fallback = [
        f"Explain the core idea of {base_topic}.",
        f"Show a step-by-step flow for {base_topic}.",
        f"What are common mistakes in {base_topic}?",
        f"Give me one real-world example of {base_topic}.",
        f"How can I practice {base_topic} in 15 minutes?",
        f"Give me a short quiz on {base_topic}.",
        f"Compare beginner vs advanced use of {base_topic}.",
        f"Create one coding task for {base_topic}.",
    ]
    random.shuffle(fallback)
    return fallback[:6]


def _svg_data_uri(svg: str) -> str:
    return f"data:image/svg+xml;utf8,{quote(svg, safe='')}"


def _visual_bar_chart_url(topic: str) -> str:
    labels = _topic_keywords(topic)[:4]
    while len(labels) < 4:
        labels.append(f"Part {len(labels)+1}")
    points = [72, 84, 90, 78]
    svg = (
        "<svg xmlns='http://www.w3.org/2000/svg' width='640' height='360' viewBox='0 0 640 360'>"
        "<rect width='640' height='360' fill='#f7f9ff'/>"
        f"<text x='24' y='36' font-size='22' font-family='Arial' fill='#22304a'>{_safe_label(topic, 34)} - Mastery</text>"
        "<line x1='60' y1='300' x2='600' y2='300' stroke='#9fb0d0' stroke-width='2'/>"
        f"<rect x='100' y='{300-points[0]*2}' width='70' height='{points[0]*2}' rx='8' fill='#4d6bff'/>"
        f"<rect x='220' y='{300-points[1]*2}' width='70' height='{points[1]*2}' rx='8' fill='#7a4dff'/>"
        f"<rect x='340' y='{300-points[2]*2}' width='70' height='{points[2]*2}' rx='8' fill='#9a27f0'/>"
        f"<rect x='460' y='{300-points[3]*2}' width='70' height='{points[3]*2}' rx='8' fill='#00a7c4'/>"
        f"<text x='96' y='325' font-size='13' font-family='Arial' fill='#22304a'>{_safe_label(labels[0], 9)}</text>"
        f"<text x='216' y='325' font-size='13' font-family='Arial' fill='#22304a'>{_safe_label(labels[1], 9)}</text>"
        f"<text x='336' y='325' font-size='13' font-family='Arial' fill='#22304a'>{_safe_label(labels[2], 9)}</text>"
        f"<text x='456' y='325' font-size='13' font-family='Arial' fill='#22304a'>{_safe_label(labels[3], 9)}</text>"
        "</svg>"
    )
    return _svg_data_uri(svg)


def _visual_mermaid_url(topic: str) -> str:
    labels = _topic_keywords(topic)
    while len(labels) < 5:
        labels.append(f"Step {len(labels)+1}")
    label = _safe_label(topic, 36)
    svg = (
        "<svg xmlns='http://www.w3.org/2000/svg' width='760' height='240' viewBox='0 0 760 240'>"
        "<rect width='760' height='240' fill='#f7f9ff'/>"
        "<defs><marker id='arr' markerWidth='10' markerHeight='10' refX='8' refY='3' orient='auto'>"
        "<path d='M0,0 L0,6 L9,3 z' fill='#4d6bff'/></marker></defs>"
        f"<rect x='20' y='82' width='120' height='56' rx='10' fill='#e8eeff' stroke='#4d6bff'/>"
        f"<text x='34' y='116' font-size='15' font-family='Arial' fill='#22304a'>{label}</text>"
        "<rect x='170' y='82' width='120' height='56' rx='10' fill='#efe8ff' stroke='#7a4dff'/>"
        f"<text x='194' y='116' font-size='15' font-family='Arial' fill='#22304a'>{_safe_label(labels[0], 12)}</text>"
        "<rect x='320' y='82' width='140' height='56' rx='10' fill='#f4e8ff' stroke='#9a27f0'/>"
        f"<text x='334' y='116' font-size='15' font-family='Arial' fill='#22304a'>{_safe_label(labels[1], 14)}</text>"
        "<rect x='490' y='82' width='110' height='56' rx='10' fill='#e8fbff' stroke='#00a7c4'/>"
        f"<text x='523' y='116' font-size='15' font-family='Arial' fill='#22304a'>{_safe_label(labels[2], 9)}</text>"
        "<rect x='630' y='82' width='110' height='56' rx='10' fill='#e7f7ee' stroke='#2ea05f'/>"
        f"<text x='650' y='116' font-size='15' font-family='Arial' fill='#22304a'>{_safe_label(labels[3], 10)}</text>"
        "<line x1='140' y1='110' x2='170' y2='110' stroke='#4d6bff' stroke-width='2.5' marker-end='url(#arr)'/>"
        "<line x1='290' y1='110' x2='320' y2='110' stroke='#4d6bff' stroke-width='2.5' marker-end='url(#arr)'/>"
        "<line x1='460' y1='110' x2='490' y2='110' stroke='#4d6bff' stroke-width='2.5' marker-end='url(#arr)'/>"
        "<line x1='600' y1='110' x2='630' y2='110' stroke='#4d6bff' stroke-width='2.5' marker-end='url(#arr)'/>"
        "</svg>"
    )
    return _svg_data_uri(svg)


def _visual_chart_url(topic: str) -> str:
    labels = _topic_keywords(topic)
    while len(labels) < 5:
        labels.append(f"Area {len(labels)+1}")
    svg = (
        "<svg xmlns='http://www.w3.org/2000/svg' width='640' height='360' viewBox='0 0 640 360'>"
        "<rect width='640' height='360' fill='#f7f9ff'/>"
        f"<text x='24' y='36' font-size='22' font-family='Arial' fill='#22304a'>{_safe_label(topic, 32)} Radar</text>"
        "<circle cx='320' cy='190' r='120' fill='none' stroke='#d8e0f5'/>"
        "<circle cx='320' cy='190' r='90' fill='none' stroke='#d8e0f5'/>"
        "<circle cx='320' cy='190' r='60' fill='none' stroke='#d8e0f5'/>"
        "<circle cx='320' cy='190' r='30' fill='none' stroke='#d8e0f5'/>"
        "<line x1='320' y1='70' x2='320' y2='310' stroke='#d8e0f5'/>"
        "<line x1='206' y1='115' x2='434' y2='265' stroke='#d8e0f5'/>"
        "<line x1='206' y1='265' x2='434' y2='115' stroke='#d8e0f5'/>"
        "<polygon points='320,82 412,142 385,244 257,244 228,159' fill='rgba(77,107,255,0.25)' stroke='#4d6bff' stroke-width='3'/>"
        f"<text x='290' y='60' font-size='14' font-family='Arial' fill='#22304a'>{_safe_label(labels[0], 10)}</text>"
        f"<text x='434' y='140' font-size='14' font-family='Arial' fill='#22304a'>{_safe_label(labels[1], 10)}</text>"
        f"<text x='412' y='270' font-size='14' font-family='Arial' fill='#22304a'>{_safe_label(labels[2], 10)}</text>"
        f"<text x='205' y='270' font-size='14' font-family='Arial' fill='#22304a'>{_safe_label(labels[3], 10)}</text>"
        f"<text x='175' y='145' font-size='14' font-family='Arial' fill='#22304a'>{_safe_label(labels[4], 10)}</text>"
        "</svg>"
    )
    return _svg_data_uri(svg)


def _visual_topic_image_url(topic: str) -> str:
    top = _safe_label(topic, 30)
    labels = _topic_keywords(topic)[:3]
    while len(labels) < 3:
        labels.append(f"Point {len(labels)+1}")
    svg = (
        "<svg xmlns='http://www.w3.org/2000/svg' width='640' height='360' viewBox='0 0 640 360'>"
        "<defs><linearGradient id='g' x1='0' x2='1' y1='0' y2='1'>"
        "<stop offset='0%' stop-color='#eef4ff'/><stop offset='100%' stop-color='#f7ebff'/></linearGradient></defs>"
        "<rect width='640' height='360' fill='url(#g)'/>"
        f"<text x='24' y='42' font-size='26' font-family='Arial' fill='#1b2a48'>{top}</text>"
        "<circle cx='120' cy='170' r='52' fill='#4d6bff22' stroke='#4d6bff' stroke-width='3'/>"
        "<circle cx='320' cy='170' r='52' fill='#7a4dff22' stroke='#7a4dff' stroke-width='3'/>"
        "<circle cx='520' cy='170' r='52' fill='#00a7c422' stroke='#00a7c4' stroke-width='3'/>"
        f"<text x='84' y='176' font-size='13' font-family='Arial' fill='#22304a'>{_safe_label(labels[0], 10)}</text>"
        f"<text x='284' y='176' font-size='13' font-family='Arial' fill='#22304a'>{_safe_label(labels[1], 10)}</text>"
        f"<text x='484' y='176' font-size='13' font-family='Arial' fill='#22304a'>{_safe_label(labels[2], 10)}</text>"
        "<line x1='172' y1='170' x2='268' y2='170' stroke='#4d6bff' stroke-width='2.5'/>"
        "<line x1='372' y1='170' x2='468' y2='170' stroke='#7a4dff' stroke-width='2.5'/>"
        "<text x='24' y='318' font-size='16' font-family='Arial' fill='#22304a'>AI Visual Map generated from your question</text>"
        "</svg>"
    )
    return _svg_data_uri(svg)


def get_quick_prompts(topic: str, style: str) -> list[str]:
    return _generate_prompt_suggestions(topic, style)


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
                "graph_image_url": _visual_chart_url(topic),
                "bar_graph_image_url": _visual_bar_chart_url(topic),
                "flowchart_image_url": _visual_mermaid_url(topic),
                "topic_image_url": _visual_topic_image_url(topic),
                "video_url": _youtube_search_url(topic),
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
