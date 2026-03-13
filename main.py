"""
BabelBot - Main Application
Multilingual Voice-to-Robot Controller

Flow:
    1. Record voice (French, Hindi, German, or English)
    2. Transcribe via Smallest.ai Pulse STT
    3. Parse command via LLM (translate + extract)
    4. Execute on Unitree Go2 via Cyberwave
    5. Voice feedback in English via Smallest.ai Waves TTS

Usage:
    python main.py              # Interactive mode (mic input)
    python main.py --test       # Test mode (typed input, no mic)
"""

import sys
import asyncio
from stt import listen_and_transcribe
from llm import parse_command
from robot import init_robot, execute
from tts import speak


BANNER = """
╔══════════════════════════════════════════════════╗
║           BabelBot - Voice Robot Controller       ║
║                                                    ║
║   Speak in French, Hindi, German, or English       ║
║   The Unitree Go2 will understand and act.         ║
║                                                    ║
║   Commands: move, turn, sit, stand, dance, wave    ║
║   Say "stop" to halt the robot                     ║
║   Press Ctrl+C to exit                             ║
╚══════════════════════════════════════════════════╝
"""


async def voice_loop():
    """
    Main voice interaction loop.
    Records from mic → transcribes → parses → executes → speaks.
    """
    print(BANNER)

    # Connect to robot
    connected = init_robot()
    if not connected:
        print("[WARN] Robot not connected. Running in mock mode.\n")

    while True:
        try:
            print("\n" + "=" * 40)
            print("[READY] Speak your command...")

            # Step 1: Listen and transcribe
            text = await listen_and_transcribe(duration=5)

            if not text.strip():
                print("[SKIP] No speech detected. Try again.")
                continue

            # Step 2: Parse command (LLM translates + extracts)
            parsed = parse_command(text)

            print(f"[PARSED] {parsed['english_translation']} → {parsed['command']}")

            # Step 3: Execute on robot
            result = execute(parsed["command"], parsed.get("params", {}))
            print(f"[RESULT] {result}")

            # Step 4: Voice feedback in English
            speak(parsed["voice_response"])

        except KeyboardInterrupt:
            print("\n[EXIT] Shutting down BabelBot.")
            break
        except Exception as e:
            print(f"[ERROR] {e}")
            continue


async def test_loop():
    """
    Test mode: type commands instead of using mic.
    Useful for debugging without audio hardware.
    """
    print(BANNER)
    print("[TEST MODE] Type commands in any language. Type 'quit' to exit.\n")

    connected = init_robot()
    if not connected:
        print("[WARN] Robot not connected. Running in mock mode.\n")

    while True:
        try:
            text = input("\n[TYPE] Your command: ").strip()

            if text.lower() in ("quit", "exit", "q"):
                print("[EXIT] Bye!")
                break

            if not text:
                continue

            # Step 2: Parse
            parsed = parse_command(text)
            print(f"[PARSED] {parsed['english_translation']} → {parsed['command']}")

            # Step 3: Execute
            result = execute(parsed["command"], parsed.get("params", {}))
            print(f"[RESULT] {result}")

            # Step 4: Speak
            speak(parsed["voice_response"])

        except KeyboardInterrupt:
            print("\n[EXIT] Bye!")
            break
        except Exception as e:
            print(f"[ERROR] {e}")
            continue


if __name__ == "__main__":
    if "--test" in sys.argv:
        asyncio.run(test_loop())
    else:
        asyncio.run(voice_loop())
