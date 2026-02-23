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


def _svg_data_uri(svg: str) -> str:
    return f"data:image/svg+xml;utf8,{quote(svg, safe='')}"


def _visual_bar_chart_url() -> str:
    svg = (
        "<svg xmlns='http://www.w3.org/2000/svg' width='640' height='360' viewBox='0 0 640 360'>"
        "<rect width='640' height='360' fill='#f7f9ff'/>"
        "<text x='24' y='36' font-size='22' font-family='Arial' fill='#22304a'>Mastery Bar Graph</text>"
        "<line x1='60' y1='300' x2='600' y2='300' stroke='#9fb0d0' stroke-width='2'/>"
        "<rect x='100' y='110' width='70' height='190' rx='8' fill='#4d6bff'/>"
        "<rect x='220' y='78' width='70' height='222' rx='8' fill='#7a4dff'/>"
        "<rect x='340' y='93' width='70' height='207' rx='8' fill='#9a27f0'/>"
        "<rect x='460' y='123' width='70' height='177' rx='8' fill='#00a7c4'/>"
        "<text x='112' y='325' font-size='15' font-family='Arial' fill='#22304a'>Concept</text>"
        "<text x='242' y='325' font-size='15' font-family='Arial' fill='#22304a'>Flow</text>"
        "<text x='347' y='325' font-size='15' font-family='Arial' fill='#22304a'>Examples</text>"
        "<text x='465' y='325' font-size='15' font-family='Arial' fill='#22304a'>Practice</text>"
        "</svg>"
    )
    return _svg_data_uri(svg)


def _visual_mermaid_url(topic: str) -> str:
    label = (topic or "Concept").strip().replace("<", "").replace(">", "")[:40]
    svg = (
        "<svg xmlns='http://www.w3.org/2000/svg' width='760' height='240' viewBox='0 0 760 240'>"
        "<rect width='760' height='240' fill='#f7f9ff'/>"
        "<defs><marker id='arr' markerWidth='10' markerHeight='10' refX='8' refY='3' orient='auto'>"
        "<path d='M0,0 L0,6 L9,3 z' fill='#4d6bff'/></marker></defs>"
        f"<rect x='20' y='82' width='120' height='56' rx='10' fill='#e8eeff' stroke='#4d6bff'/>"
        f"<text x='34' y='116' font-size='15' font-family='Arial' fill='#22304a'>{label}</text>"
        "<rect x='170' y='82' width='120' height='56' rx='10' fill='#efe8ff' stroke='#7a4dff'/>"
        "<text x='194' y='116' font-size='15' font-family='Arial' fill='#22304a'>Core Idea</text>"
        "<rect x='320' y='82' width='140' height='56' rx='10' fill='#f4e8ff' stroke='#9a27f0'/>"
        "<text x='334' y='116' font-size='15' font-family='Arial' fill='#22304a'>Step-by-step</text>"
        "<rect x='490' y='82' width='110' height='56' rx='10' fill='#e8fbff' stroke='#00a7c4'/>"
        "<text x='523' y='116' font-size='15' font-family='Arial' fill='#22304a'>Example</text>"
        "<rect x='630' y='82' width='110' height='56' rx='10' fill='#e7f7ee' stroke='#2ea05f'/>"
        "<text x='650' y='116' font-size='15' font-family='Arial' fill='#22304a'>Practice</text>"
        "<line x1='140' y1='110' x2='170' y2='110' stroke='#4d6bff' stroke-width='2.5' marker-end='url(#arr)'/>"
        "<line x1='290' y1='110' x2='320' y2='110' stroke='#4d6bff' stroke-width='2.5' marker-end='url(#arr)'/>"
        "<line x1='460' y1='110' x2='490' y2='110' stroke='#4d6bff' stroke-width='2.5' marker-end='url(#arr)'/>"
        "<line x1='600' y1='110' x2='630' y2='110' stroke='#4d6bff' stroke-width='2.5' marker-end='url(#arr)'/>"
        "</svg>"
    )
    return _svg_data_uri(svg)


def _visual_chart_url() -> str:
    svg = (
        "<svg xmlns='http://www.w3.org/2000/svg' width='640' height='360' viewBox='0 0 640 360'>"
        "<rect width='640' height='360' fill='#f7f9ff'/>"
        "<text x='24' y='36' font-size='22' font-family='Arial' fill='#22304a'>Learning Radar Graph</text>"
        "<circle cx='320' cy='190' r='120' fill='none' stroke='#d8e0f5'/>"
        "<circle cx='320' cy='190' r='90' fill='none' stroke='#d8e0f5'/>"
        "<circle cx='320' cy='190' r='60' fill='none' stroke='#d8e0f5'/>"
        "<circle cx='320' cy='190' r='30' fill='none' stroke='#d8e0f5'/>"
        "<line x1='320' y1='70' x2='320' y2='310' stroke='#d8e0f5'/>"
        "<line x1='206' y1='115' x2='434' y2='265' stroke='#d8e0f5'/>"
        "<line x1='206' y1='265' x2='434' y2='115' stroke='#d8e0f5'/>"
        "<polygon points='320,82 412,142 385,244 257,244 228,159' fill='rgba(77,107,255,0.25)' stroke='#4d6bff' stroke-width='3'/>"
        "<text x='290' y='60' font-size='14' font-family='Arial' fill='#22304a'>Concept</text>"
        "<text x='434' y='140' font-size='14' font-family='Arial' fill='#22304a'>Flow</text>"
        "<text x='412' y='270' font-size='14' font-family='Arial' fill='#22304a'>Examples</text>"
        "<text x='205' y='270' font-size='14' font-family='Arial' fill='#22304a'>Revision</text>"
        "<text x='175' y='145' font-size='14' font-family='Arial' fill='#22304a'>Practice</text>"
        "</svg>"
    )
    return _svg_data_uri(svg)


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
                "graph_image_url": _visual_chart_url(),
                "bar_graph_image_url": _visual_bar_chart_url(),
                "flowchart_image_url": _visual_mermaid_url(topic),
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
