import random
import re
from urllib.parse import quote_plus
import os

from app.services.openai_service import chatgpt_json, chatgpt_text, generate_image_data_url
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


def _title_case(text: str) -> str:
    return " ".join(part[:1].upper() + part[1:] for part in text.split() if part)


def _fallback_visual_blueprint(topic: str) -> dict:
    clean_topic = _safe_label(topic or "Learning Topic", 42)
    concepts = _topic_keywords(topic)[:4]
    while len(concepts) < 4:
        concepts.append(f"Concept {len(concepts)+1}")
    return {
        "title": clean_topic,
        "concept_nodes": concepts,
        "flow_steps": ["Understand concept", "Follow process", "Apply in example", "Practice variations", "Review errors"],
        "radar_axes": ["Concept", "Flow", "Example", "Practice", "Revision"],
        "radar_scores": [78, 86, 82, 74, 80],
        "bar_labels": ["Basics", "Process", "Examples", "Practice"],
        "bar_values": [70, 84, 79, 76],
    }


def _sanitize_labels(raw: list, min_len: int, max_len: int, max_items: int, default_prefix: str) -> list[str]:
    out = []
    for item in raw or []:
        txt = _safe_label(str(item), max_len)
        if len(txt) < min_len:
            continue
        out.append(_title_case(txt))
        if len(out) >= max_items:
            break
    while len(out) < max_items:
        out.append(f"{default_prefix} {len(out)+1}")
    return out[:max_items]


def _sanitize_scores(raw: list, max_items: int, minimum: int = 40, maximum: int = 100) -> list[int]:
    out = []
    for item in raw or []:
        try:
            num = int(item)
        except (TypeError, ValueError):
            continue
        out.append(max(minimum, min(maximum, num)))
        if len(out) >= max_items:
            break
    while len(out) < max_items:
        out.append(70 + len(out) * 4)
    return out[:max_items]


def _generate_visual_blueprint(question: str, explanation: str) -> dict:
    system_prompt = (
        "You create visual learning blueprints. Return strict JSON only with keys: "
        "title, concept_nodes, flow_steps, radar_axes, radar_scores, bar_labels, bar_values. "
        "Use concise educational phrases. No markdown."
    )
    user_prompt = (
        f"Question: {question}\n"
        f"Answer summary: {(explanation or '')[:900]}\n\n"
        "Rules:\n"
        "- concept_nodes: 4 short conceptual nodes\n"
        "- flow_steps: 5 short step-by-step actions\n"
        "- radar_axes: exactly 5 dimensions\n"
        "- radar_scores: exactly 5 integers between 50 and 95\n"
        "- bar_labels: exactly 4 labels\n"
        "- bar_values: exactly 4 integers between 50 and 95"
    )
    payload = chatgpt_json(system_prompt, user_prompt, temperature=0.4) or {}
    fallback = _fallback_visual_blueprint(question)
    # If we have explanation text, derive better fallback step labels from it.
    if explanation:
        text_lines = [line.strip(" -•\t") for line in explanation.splitlines() if line.strip()]
        sentence_parts = []
        for line in text_lines:
            sentence_parts.extend([s.strip() for s in re.split(r"[.!?]", line) if s.strip()])
        derived_steps = []
        for part in sentence_parts:
            if len(part) < 8:
                continue
            derived_steps.append(_title_case(_safe_label(part, 24)))
            if len(derived_steps) == 5:
                break
        if len(derived_steps) >= 3:
            while len(derived_steps) < 5:
                derived_steps.append(f"Apply Step {len(derived_steps)+1}")
            fallback["flow_steps"] = derived_steps[:5]
    title = _safe_label(str(payload.get("title", "")).strip() or fallback["title"], 42)
    return {
        "title": title,
        "concept_nodes": _sanitize_labels(payload.get("concept_nodes", fallback["concept_nodes"]), 3, 20, 4, "Concept"),
        "flow_steps": _sanitize_labels(payload.get("flow_steps", fallback["flow_steps"]), 3, 24, 5, "Step"),
        "radar_axes": _sanitize_labels(payload.get("radar_axes", fallback["radar_axes"]), 3, 12, 5, "Axis"),
        "radar_scores": _sanitize_scores(payload.get("radar_scores", fallback["radar_scores"]), 5, 50, 95),
        "bar_labels": _sanitize_labels(payload.get("bar_labels", fallback["bar_labels"]), 3, 12, 4, "Part"),
        "bar_values": _sanitize_scores(payload.get("bar_values", fallback["bar_values"]), 4, 50, 95),
    }


def _youtube_search_url(topic: str) -> str:
    query = f"{topic} tutorial for beginners"
    return f"https://www.youtube.com/results?search_query={quote_plus(query)}"


def _generate_ai_visual_image(question: str, blueprint: dict) -> str | None:
    enabled = os.getenv("OPENAI_VISUAL_IMAGE_ENABLED", "1").strip().lower() in {"1", "true", "yes", "on"}
    if not enabled:
        return None
    concept_line = ", ".join(blueprint.get("concept_nodes", [])[:4])
    flow_line = " -> ".join(blueprint.get("flow_steps", [])[:5])
    prompt = (
        "Create a clean educational infographic image for a programming learner. "
        "Use modern flat design, high contrast labels, readable typography, and minimal clutter. "
        "Do not include logos, watermarks, or dense paragraphs.\n\n"
        f"Topic: {question}\n"
        f"Title: {blueprint.get('title', '')}\n"
        f"Key concepts: {concept_line}\n"
        f"Learning flow: {flow_line}\n"
        "Visual layout: top title, middle concept map, bottom short takeaway strip."
    )
    return generate_image_data_url(prompt, size="1024x1024")


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


def _visual_bar_chart_url(blueprint: dict) -> str:
    labels = blueprint["bar_labels"]
    points = blueprint["bar_values"]
    svg = (
        "<svg xmlns='http://www.w3.org/2000/svg' width='640' height='360' viewBox='0 0 640 360'>"
        "<rect width='640' height='360' fill='#f7f9ff'/>"
        f"<text x='24' y='36' font-size='22' font-family='Arial' fill='#22304a'>{_safe_label(blueprint['title'], 30)} - Skill Bars</text>"
        "<line x1='60' y1='300' x2='600' y2='300' stroke='#9fb0d0' stroke-width='2'/>"
        f"<rect x='100' y='{300-int(points[0]*2)}' width='70' height='{int(points[0]*2)}' rx='8' fill='#4d6bff'/>"
        f"<rect x='220' y='{300-int(points[1]*2)}' width='70' height='{int(points[1]*2)}' rx='8' fill='#7a4dff'/>"
        f"<rect x='340' y='{300-int(points[2]*2)}' width='70' height='{int(points[2]*2)}' rx='8' fill='#9a27f0'/>"
        f"<rect x='460' y='{300-int(points[3]*2)}' width='70' height='{int(points[3]*2)}' rx='8' fill='#00a7c4'/>"
        f"<text x='96' y='325' font-size='13' font-family='Arial' fill='#22304a'>{_safe_label(labels[0], 9)}</text>"
        f"<text x='216' y='325' font-size='13' font-family='Arial' fill='#22304a'>{_safe_label(labels[1], 9)}</text>"
        f"<text x='336' y='325' font-size='13' font-family='Arial' fill='#22304a'>{_safe_label(labels[2], 9)}</text>"
        f"<text x='456' y='325' font-size='13' font-family='Arial' fill='#22304a'>{_safe_label(labels[3], 9)}</text>"
        "</svg>"
    )
    return _svg_data_uri(svg)


def _visual_mermaid_url(blueprint: dict) -> str:
    label = _safe_label(blueprint["title"], 36)
    steps = blueprint["flow_steps"]
    svg = (
        "<svg xmlns='http://www.w3.org/2000/svg' width='760' height='240' viewBox='0 0 760 240'>"
        "<rect width='760' height='240' fill='#f7f9ff'/>"
        "<defs><marker id='arr' markerWidth='10' markerHeight='10' refX='8' refY='3' orient='auto'>"
        "<path d='M0,0 L0,6 L9,3 z' fill='#4d6bff'/></marker></defs>"
        f"<rect x='20' y='82' width='120' height='56' rx='10' fill='#e8eeff' stroke='#4d6bff'/>"
        f"<text x='32' y='116' font-size='14' font-family='Arial' fill='#22304a'>{label}</text>"
        "<rect x='170' y='82' width='120' height='56' rx='10' fill='#efe8ff' stroke='#7a4dff'/>"
        f"<text x='182' y='116' font-size='14' font-family='Arial' fill='#22304a'>{_safe_label(steps[0], 14)}</text>"
        "<rect x='320' y='82' width='140' height='56' rx='10' fill='#f4e8ff' stroke='#9a27f0'/>"
        f"<text x='330' y='116' font-size='14' font-family='Arial' fill='#22304a'>{_safe_label(steps[1], 16)}</text>"
        "<rect x='490' y='82' width='110' height='56' rx='10' fill='#e8fbff' stroke='#00a7c4'/>"
        f"<text x='500' y='116' font-size='14' font-family='Arial' fill='#22304a'>{_safe_label(steps[2], 11)}</text>"
        "<rect x='630' y='82' width='110' height='56' rx='10' fill='#e7f7ee' stroke='#2ea05f'/>"
        f"<text x='640' y='116' font-size='14' font-family='Arial' fill='#22304a'>{_safe_label(steps[3], 11)}</text>"
        "<line x1='140' y1='110' x2='170' y2='110' stroke='#4d6bff' stroke-width='2.5' marker-end='url(#arr)'/>"
        "<line x1='290' y1='110' x2='320' y2='110' stroke='#4d6bff' stroke-width='2.5' marker-end='url(#arr)'/>"
        "<line x1='460' y1='110' x2='490' y2='110' stroke='#4d6bff' stroke-width='2.5' marker-end='url(#arr)'/>"
        "<line x1='600' y1='110' x2='630' y2='110' stroke='#4d6bff' stroke-width='2.5' marker-end='url(#arr)'/>"
        "</svg>"
    )
    return _svg_data_uri(svg)


def _visual_chart_url(blueprint: dict) -> str:
    labels = blueprint["radar_axes"]
    scores = blueprint["radar_scores"]

    # five-point radar coordinates around center (320,190), radius 120
    points_xy = [
        (320, 190 - int(scores[0] * 1.2)),
        (320 + int(scores[1] * 1.12), 190 - int(scores[1] * 0.36)),
        (320 + int(scores[2] * 0.7), 190 + int(scores[2] * 0.98)),
        (320 - int(scores[3] * 0.7), 190 + int(scores[3] * 0.98)),
        (320 - int(scores[4] * 1.12), 190 - int(scores[4] * 0.36)),
    ]
    poly = " ".join(f"{x},{y}" for x, y in points_xy)

    svg = (
        "<svg xmlns='http://www.w3.org/2000/svg' width='640' height='360' viewBox='0 0 640 360'>"
        "<rect width='640' height='360' fill='#f7f9ff'/>"
        f"<text x='24' y='36' font-size='22' font-family='Arial' fill='#22304a'>{_safe_label(blueprint['title'], 32)} Radar</text>"
        "<circle cx='320' cy='190' r='120' fill='none' stroke='#d8e0f5'/>"
        "<circle cx='320' cy='190' r='90' fill='none' stroke='#d8e0f5'/>"
        "<circle cx='320' cy='190' r='60' fill='none' stroke='#d8e0f5'/>"
        "<circle cx='320' cy='190' r='30' fill='none' stroke='#d8e0f5'/>"
        "<line x1='320' y1='70' x2='320' y2='310' stroke='#d8e0f5'/>"
        "<line x1='206' y1='115' x2='434' y2='265' stroke='#d8e0f5'/>"
        "<line x1='206' y1='265' x2='434' y2='115' stroke='#d8e0f5'/>"
        f"<polygon points='{poly}' fill='rgba(77,107,255,0.25)' stroke='#4d6bff' stroke-width='3'/>"
        f"<text x='290' y='60' font-size='14' font-family='Arial' fill='#22304a'>{_safe_label(labels[0], 10)}</text>"
        f"<text x='434' y='140' font-size='14' font-family='Arial' fill='#22304a'>{_safe_label(labels[1], 10)}</text>"
        f"<text x='412' y='270' font-size='14' font-family='Arial' fill='#22304a'>{_safe_label(labels[2], 10)}</text>"
        f"<text x='205' y='270' font-size='14' font-family='Arial' fill='#22304a'>{_safe_label(labels[3], 10)}</text>"
        f"<text x='175' y='145' font-size='14' font-family='Arial' fill='#22304a'>{_safe_label(labels[4], 10)}</text>"
        "</svg>"
    )
    return _svg_data_uri(svg)


def _visual_topic_image_url(blueprint: dict) -> str:
    top = _safe_label(blueprint["title"], 30)
    labels = blueprint["concept_nodes"][:3]
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
        blueprint = _generate_visual_blueprint(question, text)
        ai_visual_image_url = _generate_ai_visual_image(question, blueprint)
        return {
            "response_type": "visual",
            "ai_used": ai_used,
            "text": text,
            "assets": {
                "ai_image_url": ai_visual_image_url,
                "diagram": " -> ".join(blueprint["flow_steps"]),
                "graph_image_url": _visual_chart_url(blueprint),
                "bar_graph_image_url": _visual_bar_chart_url(blueprint),
                "flowchart_image_url": _visual_mermaid_url(blueprint),
                "topic_image_url": _visual_topic_image_url(blueprint),
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
