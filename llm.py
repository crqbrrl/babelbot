"""
BabelBot - LLM Command Parser
Handles: multilingual text → English translation + robot command extraction
"""

import json
from openai import OpenAI
from config import OPENAI_API_KEY, LLM_MODEL, LLM_TEMPERATURE, VALID_COMMANDS


SYSTEM_PROMPT = """You are a multilingual robot command interpreter for a Unitree Go2 robot dog.

You receive voice commands in ANY language (French, Hindi, German, English, or mixed).
Your job:
1. Understand the intent regardless of language
2. Map it to one of the valid robot commands
3. Return structured JSON

Valid commands:
{commands}

ALWAYS respond with this exact JSON:
{{
    "original_text": "what the user said (as transcribed)",
    "english_translation": "English translation",
    "command": "one of the valid command keys",
    "params": {{}},
    "voice_response": "Short English sentence to confirm the action (max 10 words)"
}}

Rules:
- If the user says a distance (e.g. "2 steps", "1 meter"), include {{"distance": <number>}}
- If the user says a direction with angle, include {{"angle": <degrees>}}
- If the command is unclear, use "stop" and explain in voice_response
- Keep voice_response SHORT and natural (like a teammate confirming)

Examples:
- "Avance" → {{"original_text": "Avance", "english_translation": "Move forward", "command": "move_forward", "params": {{"distance": 1}}, "voice_response": "Moving forward"}}
- "बैठ जाओ" → {{"original_text": "बैठ जाओ", "english_translation": "Sit down", "command": "sit", "params": {{}}, "voice_response": "Sitting down now"}}
- "Dreh dich nach links" → {{"original_text": "Dreh dich nach links", "english_translation": "Turn left", "command": "turn_left", "params": {{"angle": 90}}, "voice_response": "Turning left"}}
- "Do a little dance" → {{"original_text": "Do a little dance", "english_translation": "Do a little dance", "command": "dance", "params": {{}}, "voice_response": "Let me dance for you"}}
"""


client = OpenAI(api_key=OPENAI_API_KEY)


def parse_command(transcribed_text: str) -> dict:
    """
    Send transcribed text (any language) to LLM.
    Returns structured command with English translation.

    Args:
        transcribed_text: Raw text from STT (could be FR, HI, DE, EN)

    Returns:
        dict with keys: original_text, english_translation, command, params, voice_response
    """
    commands_str = json.dumps(
        {k: v["description"] for k, v in VALID_COMMANDS.items()},
        indent=2,
    )

    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT.format(commands=commands_str),
            },
            {
                "role": "user",
                "content": transcribed_text,
            },
        ],
        response_format={"type": "json_object"},
        temperature=LLM_TEMPERATURE,
    )

    result = json.loads(response.choices[0].message.content)

    # Validate command exists
    if result.get("command") not in VALID_COMMANDS:
        result["command"] = "stop"
        result["voice_response"] = "I didn't understand that command."

    print(f"[LLM] {result['original_text']} → {result['command']}")
    return result


# ============================================================
# Quick test
# ============================================================
if __name__ == "__main__":
    # Test with different languages
    test_inputs = [
        "Avance de trois pas",          # French
        "बाएं मुड़ो",                      # Hindi
        "Sitz!",                          # German
        "Move forward and then sit",      # English
    ]

    for text in test_inputs:
        print(f"\nInput: {text}")
        result = parse_command(text)
        print(f"Output: {json.dumps(result, indent=2, ensure_ascii=False)}")
