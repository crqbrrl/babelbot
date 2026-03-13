"""
BabelBot - Test: TTS Output + Robot Execution
Tests the output side of the pipeline: LLM result → Robot executes → TTS speaks.

This is the "action" half of the system. The input half (STT → LLM) is tested
in test_speech_to_command.py. This file tests what happens AFTER the command
is parsed: does the robot move AND does it speak back correctly?

4 test modes:
    1. MOCK        → Run commands with mock robot + mock TTS (no API keys needed)
    2. TTS ONLY    → Test voice output without robot (needs SMALLEST_API_KEY)
    3. FULL CHAIN  → Type text → LLM → Robot executes → TTS speaks (needs OpenAI + Smallest keys)
    4. DEMO RUN    → Simulate the hackathon demo with all 3 languages

Usage:
    python test_tts_to_robot.py                # Mock mode (no keys needed)
    python test_tts_to_robot.py --tts          # Test TTS output only
    python test_tts_to_robot.py --full         # Full chain: text → LLM → Robot → TTS
    python test_tts_to_robot.py --demo         # Run the hackathon demo sequence
"""

import sys
import json
import time
from robot import init_robot, execute, get_robot_status
from tts import speak
from llm import parse_command
from config import VALID_COMMANDS


# ============================================================
# TEST 1: Mock robot + mock TTS (no API keys)
# ============================================================
def test_mock_robot_and_tts():
    """
    Simulate the robot executing commands and generating voice responses.
    No API keys needed — prints what WOULD happen.
    """
    print("=" * 55)
    print("  TEST: Robot Execute → TTS Output (Mock Mode)")
    print("  No API keys needed")
    print("=" * 55)

    # Simulate what the LLM would return for each command
    simulated_llm_outputs = [
        {
            "original_text": "Avance de deux pas",
            "english_translation": "Move forward two steps",
            "command": "move_forward",
            "params": {"distance": 2},
            "voice_response": "Moving forward two steps",
        },
        {
            "original_text": "बाएं मुड़ो",
            "english_translation": "Turn left",
            "command": "turn_left",
            "params": {"angle": 90},
            "voice_response": "Turning left",
        },
        {
            "original_text": "Sitz!",
            "english_translation": "Sit down",
            "command": "sit",
            "params": {},
            "voice_response": "Sitting down now",
        },
        {
            "original_text": "Steh auf",
            "english_translation": "Stand up",
            "command": "stand",
            "params": {},
            "voice_response": "Standing up",
        },
        {
            "original_text": "Fais une danse",
            "english_translation": "Do a dance",
            "command": "dance",
            "params": {},
            "voice_response": "Let me dance for you",
        },
        {
            "original_text": "Gib Pfote",
            "english_translation": "Shake hands",
            "command": "shake_hand",
            "params": {},
            "voice_response": "Shaking your hand",
        },
        {
            "original_text": "Stop",
            "english_translation": "Stop",
            "command": "stop",
            "params": {},
            "voice_response": "Stopping all movement",
        },
    ]

    print(f"\nRunning {len(simulated_llm_outputs)} simulated commands...\n")
    print(f"{'Input':<25} {'Command':<16} {'Robot Result':<25} {'TTS Would Say'}")
    print("-" * 90)

    passed = 0

    for llm_output in simulated_llm_outputs:
        # Step 1: Robot executes
        robot_result = execute(llm_output["command"], llm_output.get("params", {}))

        # Step 2: TTS would speak (mock — just print)
        tts_text = llm_output["voice_response"]

        print(
            f"{llm_output['original_text']:<25} "
            f"{llm_output['command']:<16} "
            f"{robot_result[:23]:<25} "
            f"\"{tts_text}\""
        )
        passed += 1

    print("-" * 90)
    print(f"\n[MOCK] All {passed} commands executed successfully")
    print("[MOCK] TTS responses generated (not played — use --tts to hear them)")


# ============================================================
# TEST 2: TTS output only (test the voice)
# ============================================================
def test_tts_output():
    """
    Test Smallest.ai TTS with the exact phrases the robot would say.
    Needs SMALLEST_API_KEY.
    """
    print("=" * 55)
    print("  TEST: TTS Voice Output")
    print("  Needs: SMALLEST_API_KEY")
    print("=" * 55)

    test_phrases = [
        "Moving forward two steps",
        "Turning left ninety degrees",
        "Sitting down now",
        "Standing up",
        "Let me dance for you",
        "Shaking your hand",
        "Stopping all movement",
        "I didn't understand that command",
        "Command received. Moving backward one step.",
        "Turning right forty five degrees",
    ]

    print(f"\nPlaying {len(test_phrases)} TTS phrases...\n")

    for i, phrase in enumerate(test_phrases, 1):
        print(f"[{i}/{len(test_phrases)}] Speaking: \"{phrase}\"")
        t0 = time.time()
        filepath = speak(phrase, play=True)
        elapsed = time.time() - t0
        status = "OK" if filepath else "FALLBACK"
        print(f"  → {status} ({elapsed:.2f}s)\n")

    print("[DONE] TTS test complete")


# ============================================================
# TEST 3: Full chain — text → LLM → Robot → TTS
# ============================================================
def test_full_chain():
    """
    Type a command in any language.
    LLM parses → Robot executes → TTS speaks the confirmation.
    This tests the entire output pipeline end-to-end.

    Needs: OPENAI_API_KEY + SMALLEST_API_KEY
    """
    print("=" * 55)
    print("  TEST: Full Output Chain (LLM → Robot → TTS)")
    print("  Type commands in French, Hindi, German, or English")
    print("  Type 'quit' to exit")
    print("=" * 55)

    # Init robot (will run in mock if no Cyberwave key)
    connected = init_robot()
    if not connected:
        print("[INFO] Robot in mock mode\n")

    results = []
    round_num = 0

    while True:
        try:
            text = input("\n[TYPE] Voice command: ").strip()

            if text.lower() in ("quit", "exit", "q"):
                break
            if not text:
                continue

            round_num += 1
            print(f"\n--- Round {round_num} ---")

            # Step 1: LLM parses
            t0 = time.time()
            parsed = parse_command(text)
            llm_time = time.time() - t0

            # Step 2: Robot executes
            t1 = time.time()
            robot_result = execute(parsed["command"], parsed.get("params", {}))
            robot_time = time.time() - t1

            # Step 3: TTS speaks
            t2 = time.time()
            voice_text = parsed.get("voice_response", "Done")
            speak(voice_text, play=True)
            tts_time = time.time() - t2

            # Display full result
            total = llm_time + robot_time + tts_time
            print(f"\n┌──────────────────────────────────────────────────┐")
            print(f"│ Input:        {text}")
            print(f"│ English:      {parsed.get('english_translation', '?')}")
            print(f"│ Command:      {parsed['command']} {json.dumps(parsed.get('params', {}))}")
            print(f"│ Robot:        {robot_result}")
            print(f"│ TTS spoke:    \"{voice_text}\"")
            print(f"│ Timing:       LLM {llm_time:.2f}s + Robot {robot_time:.4f}s + TTS {tts_time:.2f}s = {total:.2f}s")
            print(f"└──────────────────────────────────────────────────┘")

            results.append({
                "round": round_num,
                "input": text,
                "command": parsed["command"],
                "voice": voice_text,
                "total_time": total,
            })

        except KeyboardInterrupt:
            break

    if results:
        print("\n" + "=" * 50)
        print("  SESSION SUMMARY")
        print("=" * 50)
        for r in results:
            print(f"  #{r['round']}: \"{r['input']}\" → {r['command']} → \"{r['voice']}\" ({r['total_time']:.2f}s)")
        avg = sum(r["total_time"] for r in results) / len(results)
        print(f"\n  Avg total latency: {avg:.2f}s")


# ============================================================
# TEST 4: Demo sequence (all 3 languages, robot + TTS)
# ============================================================
def test_demo_run():
    """
    Simulate the exact hackathon demo:
    3 speakers, 3 languages, robot acts + speaks after each command.

    Needs: OPENAI_API_KEY + SMALLEST_API_KEY
    """
    print("=" * 55)
    print("  DEMO RUN: Hackathon Presentation Simulation")
    print("  3 speakers, 3 languages, 1 robot dog")
    print("=" * 55)

    connected = init_robot()
    if not connected:
        print("[INFO] Robot in mock mode — voice output still works\n")

    demo_steps = [
        {"speaker": "Cyriaque",  "lang": "FR", "text": "Avance tout droit"},
        {"speaker": "Cyriaque",  "lang": "FR", "text": "Tourne a gauche"},
        {"speaker": "Dev 1",     "lang": "HI", "text": "आगे बढ़ो तीन कदम"},
        {"speaker": "Dev 1",     "lang": "HI", "text": "बैठ जाओ"},
        {"speaker": "Dev 2",     "lang": "DE", "text": "Steh auf"},
        {"speaker": "Dev 2",     "lang": "DE", "text": "Tanz fur uns"},
        {"speaker": "Everyone",  "lang": "EN", "text": "Stop"},
    ]

    total_time = 0

    for i, step in enumerate(demo_steps, 1):
        print(f"\n{'='*55}")
        print(f"  Step {i}/{len(demo_steps)}")
        print(f"  Speaker: {step['speaker']} ({step['lang']})")
        print(f"  Says: \"{step['text']}\"")
        print(f"{'='*55}")

        # LLM parse
        t0 = time.time()
        parsed = parse_command(step["text"])
        llm_time = time.time() - t0

        # Robot execute
        t1 = time.time()
        robot_result = execute(parsed["command"], parsed.get("params", {}))
        robot_time = time.time() - t1

        # TTS speak
        t2 = time.time()
        voice_text = parsed.get("voice_response", "Done")
        speak(voice_text, play=True)
        tts_time = time.time() - t2

        step_total = llm_time + robot_time + tts_time
        total_time += step_total

        print(f"\n  Translation:  {parsed.get('english_translation', '?')}")
        print(f"  Command:      {parsed['command']} {json.dumps(parsed.get('params', {}))}")
        print(f"  Robot:        {robot_result}")
        print(f"  Robot said:   \"{voice_text}\"")
        print(f"  Latency:      {step_total:.2f}s (LLM {llm_time:.2f} + Robot {robot_time:.4f} + TTS {tts_time:.2f})")

        # Pause between steps like a real demo
        if i < len(demo_steps):
            print(f"\n  [pause 2s before next speaker...]")
            time.sleep(2)

    print(f"\n{'='*55}")
    print(f"  DEMO COMPLETE")
    print(f"  Total time: {total_time:.2f}s for {len(demo_steps)} commands")
    print(f"  Avg latency per command: {total_time / len(demo_steps):.2f}s")
    print(f"{'='*55}")


# ============================================================
# ENTRY POINT
# ============================================================
if __name__ == "__main__":
    if "--tts" in sys.argv:
        test_tts_output()

    elif "--full" in sys.argv:
        test_full_chain()

    elif "--demo" in sys.argv:
        test_demo_run()

    else:
        test_mock_robot_and_tts()
