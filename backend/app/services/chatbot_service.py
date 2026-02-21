def generate_adaptive_response(question: str, style: str) -> dict:
    topic = question.strip().rstrip("?")

    if style == "visual":
        text = (
            f"Visual Learning Plan for: {topic}\n\n"
            "1. Big Picture\n"
            "- Start with a concept diagram and identify key entities.\n\n"
            "2. Process Flow\n"
            "- Follow the sequence from input to output and mark error paths.\n\n"
            "3. Worked Example\n"
            "- Read one solved example and trace each step visually.\n\n"
            "4. Revision Snapshot\n"
            "- Use a one-page visual summary with keywords and arrows."
        )
        return {
            "response_type": "visual",
            "text": text,
            "assets": {
                "diagram": "Input -> Try Block -> Exception Raised? -> Catch -> Finally -> Continue",
                "video_url": "https://www.youtube.com/watch?v=1XAfapkBQjk",
                "gif_url": "https://media.giphy.com/media/26ufdipQqU2lhNA4g/giphy.gif",
                "suggested_downloads": ["pdf", "video"],
            },
        }

    if style == "auditory":
        script = (
            f"Audio-style explanation for {topic}. "
            "Think of exception handling as a safety system. "
            "The try block runs risky code. If an issue occurs, catch handles it clearly. "
            "Finally runs cleanup steps no matter what happens."
        )
        return {
            "response_type": "auditory",
            "text": (
                f"Auditory Learning Script for: {topic}\n\n"
                "- Listen to this in short chunks.\n"
                "- Repeat each point out loud in your own words.\n"
                "- Record a 30-second summary after each section."
            ),
            "assets": {
                "audio_script": script,
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
        "text": (
            f"Kinesthetic Practice Path for: {topic}\n\n"
            "Step 1: Create class and main method.\n"
            "Step 2: Put risky operation inside try block.\n"
            "Step 3: Add specific catch block and print readable message.\n"
            "Step 4: Add finally block and run code.\n"
            "Step 5: Modify input to trigger another exception and test again."
        ),
        "assets": {
            "starter_code": starter_code,
            "task_sheet": "Implement try-catch-finally and test two failure cases.",
            "suggested_downloads": ["task_sheet", "solution"],
        },
    }
