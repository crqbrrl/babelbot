"""
BabelBot - Configuration
All API keys, constants, and settings in one place.
"""

import os

# ============================================================
# API KEYS (set as environment variables)
# ============================================================
SMALLEST_API_KEY = os.environ.get("SMALLEST_API_KEY", "")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
CYBERWAVE_API_KEY = os.environ.get("CYBERWAVE_API_KEY", "")

# ============================================================
# SMALLEST.AI CONFIG
# ============================================================
STT_WS_URL = "wss://waves-api.smallest.ai/api/v1/pulse/get_text"
STT_REST_URL = "https://waves-api.smallest.ai/api/v1/pulse/get_text"
TTS_VOICE_ID = "emily"
TTS_MODEL = "lightning"
TTS_SPEED = 1.2  # slightly faster for snappy robot feedback

# ============================================================
# AUDIO CONFIG (microphone)
# ============================================================
SAMPLE_RATE = 16000
CHANNELS = 1
CHUNK_SIZE = 1024
RECORD_SECONDS = 5  # default recording duration

# ============================================================
# CYBERWAVE CONFIG
# ============================================================
ROBOT_ASSET_ID = "unitree/go2"  # adjust based on what's available at hackathon
ENVIRONMENT_ID = os.environ.get("CYBERWAVE_ENVIRONMENT_ID", "")

# ============================================================
# LLM CONFIG
# ============================================================
LLM_MODEL = "gpt-4o-mini"  # fast + cheap for hackathon
LLM_TEMPERATURE = 0

# ============================================================
# SUPPORTED LANGUAGES
# ============================================================
TEAM_LANGUAGES = {
    "cyriaque": "fr",  # French
    "dev1": "hi",       # Hindi
    "dev2": "de",       # German (Austrian)
}

# ============================================================
# ROBOT COMMANDS
# ============================================================
VALID_COMMANDS = {
    "move_forward": {
        "description": "Move the dog forward",
        "params": ["distance"],
    },
    "move_backward": {
        "description": "Move the dog backward",
        "params": ["distance"],
    },
    "turn_left": {
        "description": "Turn the dog left",
        "params": ["angle"],
    },
    "turn_right": {
        "description": "Turn the dog right",
        "params": ["angle"],
    },
    "sit": {
        "description": "Make the dog sit down",
        "params": [],
    },
    "stand": {
        "description": "Make the dog stand up",
        "params": [],
    },
    "wave": {
        "description": "Make the dog wave a paw",
        "params": [],
    },
    "dance": {
        "description": "Make the dog do a dance",
        "params": [],
    },
    "stop": {
        "description": "Stop all movement",
        "params": [],
    },
    "shake_hand": {
        "description": "Make the dog shake hands",
        "params": [],
    },
}
