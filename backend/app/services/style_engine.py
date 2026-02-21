from collections import Counter


QUESTIONS = [
    {
        "id": 1,
        "question": "When learning a new chapter, what helps you most?",
        "options": [
            {"key": "A", "text": "Mind maps and diagrams", "style": "visual"},
            {"key": "B", "text": "Teacher explanation and discussion", "style": "auditory"},
            {"key": "C", "text": "Trying examples hands-on", "style": "kinesthetic"},
        ],
    },
    {
        "id": 2,
        "question": "How do you remember steps best?",
        "options": [
            {"key": "A", "text": "By seeing them written as a flow", "style": "visual"},
            {"key": "B", "text": "By hearing them repeated", "style": "auditory"},
            {"key": "C", "text": "By performing them", "style": "kinesthetic"},
        ],
    },
    {
        "id": 3,
        "question": "In class, you focus more on:",
        "options": [
            {"key": "A", "text": "Slides/charts on screen", "style": "visual"},
            {"key": "B", "text": "Instructor voice and tone", "style": "auditory"},
            {"key": "C", "text": "Activities and demos", "style": "kinesthetic"},
        ],
    },
    {
        "id": 4,
        "question": "When stuck on a concept, you prefer:",
        "options": [
            {"key": "A", "text": "An infographic", "style": "visual"},
            {"key": "B", "text": "A spoken walkthrough", "style": "auditory"},
            {"key": "C", "text": "A small practice task", "style": "kinesthetic"},
        ],
    },
    {
        "id": 5,
        "question": "Your best revision method is:",
        "options": [
            {"key": "A", "text": "Color-coded notes", "style": "visual"},
            {"key": "B", "text": "Reading aloud", "style": "auditory"},
            {"key": "C", "text": "Solving practice sets", "style": "kinesthetic"},
        ],
    },
    {
        "id": 6,
        "question": "You follow instructions faster when they are:",
        "options": [
            {"key": "A", "text": "Shown as screenshots", "style": "visual"},
            {"key": "B", "text": "Explained verbally", "style": "auditory"},
            {"key": "C", "text": "Given while doing", "style": "kinesthetic"},
        ],
    },
    {
        "id": 7,
        "question": "To learn software tools, you prefer:",
        "options": [
            {"key": "A", "text": "Watching UI tutorials", "style": "visual"},
            {"key": "B", "text": "Listening to a trainer", "style": "auditory"},
            {"key": "C", "text": "Using it yourself", "style": "kinesthetic"},
        ],
    },
    {
        "id": 8,
        "question": "Which resource do you open first?",
        "options": [
            {"key": "A", "text": "Charts/notes", "style": "visual"},
            {"key": "B", "text": "Podcast/lecture", "style": "auditory"},
            {"key": "C", "text": "Practice worksheet", "style": "kinesthetic"},
        ],
    },
    {
        "id": 9,
        "question": "You learn coding concepts fastest by:",
        "options": [
            {"key": "A", "text": "Seeing code flow diagrams", "style": "visual"},
            {"key": "B", "text": "Hearing logic explained", "style": "auditory"},
            {"key": "C", "text": "Editing/running code", "style": "kinesthetic"},
        ],
    },
    {
        "id": 10,
        "question": "What keeps you engaged longest?",
        "options": [
            {"key": "A", "text": "Animated visuals", "style": "visual"},
            {"key": "B", "text": "Interactive discussion", "style": "auditory"},
            {"key": "C", "text": "Lab challenge", "style": "kinesthetic"},
        ],
    },
    {
        "id": 11,
        "question": "During exam prep, you depend on:",
        "options": [
            {"key": "A", "text": "Summary charts", "style": "visual"},
            {"key": "B", "text": "Recorded explanations", "style": "auditory"},
            {"key": "C", "text": "Mock tests", "style": "kinesthetic"},
        ],
    },
    {
        "id": 12,
        "question": "A teacher should ideally:",
        "options": [
            {"key": "A", "text": "Use diagrams in every topic", "style": "visual"},
            {"key": "B", "text": "Explain clearly with examples", "style": "auditory"},
            {"key": "C", "text": "Give mini exercises", "style": "kinesthetic"},
        ],
    },
    {
        "id": 13,
        "question": "When learning algorithms, you prefer:",
        "options": [
            {"key": "A", "text": "Flowcharts", "style": "visual"},
            {"key": "B", "text": "Story-like explanation", "style": "auditory"},
            {"key": "C", "text": "Implementing algorithm", "style": "kinesthetic"},
        ],
    },
    {
        "id": 14,
        "question": "You retain information better when:",
        "options": [
            {"key": "A", "text": "You see it", "style": "visual"},
            {"key": "B", "text": "You hear it", "style": "auditory"},
            {"key": "C", "text": "You do it", "style": "kinesthetic"},
        ],
    },
    {
        "id": 15,
        "question": "For difficult topics, you request:",
        "options": [
            {"key": "A", "text": "Visual cheat sheet", "style": "visual"},
            {"key": "B", "text": "Audio explanation", "style": "auditory"},
            {"key": "C", "text": "Practice worksheet", "style": "kinesthetic"},
        ],
    },
    {
        "id": 16,
        "question": "What makes online learning easier for you?",
        "options": [
            {"key": "A", "text": "Video with diagrams", "style": "visual"},
            {"key": "B", "text": "Clear narration", "style": "auditory"},
            {"key": "C", "text": "Interactive tasks", "style": "kinesthetic"},
        ],
    },
    {
        "id": 17,
        "question": "You are most confident after:",
        "options": [
            {"key": "A", "text": "Reviewing visuals", "style": "visual"},
            {"key": "B", "text": "Explaining aloud", "style": "auditory"},
            {"key": "C", "text": "Completing practice", "style": "kinesthetic"},
        ],
    },
    {
        "id": 18,
        "question": "To understand exception handling, you prefer:",
        "options": [
            {"key": "A", "text": "Exception flow diagram", "style": "visual"},
            {"key": "B", "text": "Audio lesson", "style": "auditory"},
            {"key": "C", "text": "Write and run try-catch code", "style": "kinesthetic"},
        ],
    },
    {
        "id": 19,
        "question": "Which learning environment suits you best?",
        "options": [
            {"key": "A", "text": "Slides and whiteboard", "style": "visual"},
            {"key": "B", "text": "Discussion room", "style": "auditory"},
            {"key": "C", "text": "Lab/workshop", "style": "kinesthetic"},
        ],
    },
    {
        "id": 20,
        "question": "How do you prefer final revision?",
        "options": [
            {"key": "A", "text": "One-page visual map", "style": "visual"},
            {"key": "B", "text": "Listen to summary notes", "style": "auditory"},
            {"key": "C", "text": "Solve timed exercises", "style": "kinesthetic"},
        ],
    },
]


def evaluate_style(answer_styles: list[str]) -> dict:
    counts = Counter(answer_styles)
    visual = counts.get("visual", 0)
    auditory = counts.get("auditory", 0)
    kinesthetic = counts.get("kinesthetic", 0)

    scores = {
        "visual": visual,
        "auditory": auditory,
        "kinesthetic": kinesthetic,
    }

    winner = sorted(scores.items(), key=lambda item: (-item[1], item[0]))[0][0]

    return {
        "learning_style": winner,
        "visual_score": visual,
        "auditory_score": auditory,
        "kinesthetic_score": kinesthetic,
    }
