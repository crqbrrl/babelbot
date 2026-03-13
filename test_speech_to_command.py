"""
BabelBot - Test: STT → LLM Pipeline
Tests the full speech-to-command chain WITHOUT the robot.

3 test modes:
    1. LIVE MIC   → Record your voice → STT → LLM → see parsed command
    2. AUDIO FILE  → Load a .wav file → STT → LLM → see parsed command
    3. MOCK TEXT   → Skip STT, type text in any language → LLM → see parsed command

Usage:
    python test_speech_to_command.py              # Live mic mode
    python test_speech_to_command.py --file audio.wav  # From audio file
    python test_speech_to_command.py --mock        # Type text, skip mic
"""

import sys
import json
import asyncio
import time
from stt import listen_and_transcribe, transcribe_streaming, transcribe_rest, raw_to_wav
from llm import parse_command


# ============================================================
# TEST 1: Live mic → STT → LLM
# ============================================================
async def test_live_mic():
    """
    Record from your mic, transcribe, then parse the command.
    Lets you test all 3 languages live.
    """
    print("=" * 50)
    print("  TEST: Live Mic → STT → LLM")
    print("  Speak in French, Hindi, German, or English")
    print("  Press Ctrl+C to stop")
    print("=" * 50)

    round_num = 0
    results = []

    while True:
        try:
            round_num += 1
            print(f"\n--- Round {round_num} ---")
            print("[MIC] Speak your command now...")

            # Step 1: Record + transcribe
            t0 = time.time()
            transcribed = await listen_and_transcribe(duration=5)
            stt_time = time.time() - t0

            if not transcribed.strip():
                print("[SKIP] No speech detected. Try again.\n")
                continue

            print(f"[STT] Got: \"{transcribed}\" ({stt_time:.2f}s)")

            # Step 2: Parse via LLM
            t1 = time.time()
            parsed = parse_command(transcribed)
            llm_time = time.time() - t1

            # Step 3: Display results
            print_result(transcribed, parsed, stt_time, llm_time)
            results.append({
                "round": round_num,
                "input": transcribed,
                "parsed": parsed,
                "stt_time": stt_time,
                "llm_time": llm_time,
            })

        except KeyboardInterrupt:
            print("\n\n" + "=" * 50)
            print("  TEST SUMMARY")
            print("=" * 50)
            print_summary(results)
            break


# ============================================================
# TEST 2: Audio file → STT → LLM
# ============================================================
async def test_audio_file(filepath: str):
    """
    Load a WAV file, send it to STT, then parse the command.
    Useful for repeatable tests with pre-recorded audio.
    """
    print(f"[FILE] Loading: {filepath}")

    try:
        with open(filepath, "rb") as f:
            audio_data = f.read()
    except FileNotFoundError:
        print(f"[ERROR] File not found: {filepath}")
        return

    print(f"[FILE] Loaded {len(audio_data)} bytes")

    # Step 1: Transcribe
    t0 = time.time()
    transcribed = await transcribe_rest(audio_data)
    stt_time = time.time() - t0

    if not transcribed.strip():
        print("[ERROR] STT returned empty text. Check the audio file or API key.")
        return

    print(f"[STT] Got: \"{transcribed}\" ({stt_time:.2f}s)")

    # Step 2: Parse
    t1 = time.time()
    parsed = parse_command(transcribed)
    llm_time = time.time() - t1

    # Step 3: Display
    print_result(transcribed, parsed, stt_time, llm_time)


# ============================================================
# TEST 3: Mock text → LLM (skip STT entirely)
# ============================================================
async def test_mock_text():
    """
    Type commands in any language. Tests only the LLM parsing.
    No mic or API key for Smallest.ai needed.
    Only needs OPENAI_API_KEY.
    """
    print("=" * 50)
    print("  TEST: Mock Text → LLM (no mic needed)")
    print("  Type commands in French, Hindi, German, or English")
    print("  Type 'quit' to exit, 'batch' for preset tests")
    print("=" * 50)

    results = []
    round_num = 0

    while True:
        try:
            text = input("\n[TYPE] Your command: ").strip()

            if text.lower() in ("quit", "exit", "q"):
                break

            if text.lower() == "batch":
                await run_batch_tests()
                continue

            if not text:
                continue

            round_num += 1
            t0 = time.time()
            parsed = parse_command(text)
            llm_time = time.time() - t0

            print_result(text, parsed, stt_time=0, llm_time=llm_time)
            results.append({
                "round": round_num,
                "input": text,
                "parsed": parsed,
                "llm_time": llm_time,
            })

        except KeyboardInterrupt:
            break

    print("\n" + "=" * 50)
    print("  TEST SUMMARY")
    print("=" * 50)
    print_summary(results)


# ============================================================
# BATCH: Preset test cases for all 3 languages
# ============================================================
async def run_batch_tests():
    """
    Run preset commands in all team languages.
    Good for verifying LLM handles each language correctly.
    """
    test_cases = [
        # French (Cyriaque)
        {"lang": "FR", "text": "Avance"},
        {"lang": "FR", "text": "Recule de deux pas"},
        {"lang": "FR", "text": "Tourne a gauche"},
        {"lang": "FR", "text": "Assis"},
        {"lang": "FR", "text": "Fais une danse"},

        # Hindi (Dev 1)
        {"lang": "HI", "text": "आगे बढ़ो"},
        {"lang": "HI", "text": "बाएं मुड़ो"},
        {"lang": "HI", "text": "बैठ जाओ"},
        {"lang": "HI", "text": "खड़े हो जाओ"},
        {"lang": "HI", "text": "हाथ मिलाओ"},

        # German (Dev 2)
        {"lang": "DE", "text": "Vorwarts"},
        {"lang": "DE", "text": "Dreh dich nach links"},
        {"lang": "DE", "text": "Sitz"},
        {"lang": "DE", "text": "Steh auf"},
        {"lang": "DE", "text": "Tanz"},

        # English (fallback)
        {"lang": "EN", "text": "Move forward three steps"},
        {"lang": "EN", "text": "Turn right 45 degrees"},
        {"lang": "EN", "text": "Sit down boy"},
        {"lang": "EN", "text": "Do a little dance"},
        {"lang": "EN", "text": "Stop"},

        # Edge cases
        {"lang": "MIX", "text": "Avance forward please"},
        {"lang": "MIX", "text": "Go left, nein rechts"},
        {"lang": "??", "text": "blahblah gibberish xyz"},
    ]

    print(f"\n[BATCH] Running {len(test_cases)} test cases...\n")
    print(f"{'Lang':<6} {'Input':<30} {'Command':<16} {'Translation':<30} {'Time':<6}")
    print("-" * 90)

    passed = 0
    failed = 0

    for case in test_cases:
        try:
            t0 = time.time()
            parsed = parse_command(case["text"])
            elapsed = time.time() - t0

            cmd = parsed.get("command", "???")
            translation = parsed.get("english_translation", "???")[:28]

            # Basic validation: did it return a valid command?
            is_valid = cmd in [
                "move_forward", "move_backward", "turn_left", "turn_right",
                "sit", "stand", "wave", "dance", "stop", "shake_hand",
            ]

            status = "OK" if is_valid else "FAIL"
            if is_valid:
                passed += 1
            else:
                failed += 1

            print(f"{case['lang']:<6} {case['text']:<30} {cmd:<16} {translation:<30} {elapsed:.2f}s  {status}")

        except Exception as e:
            failed += 1
            print(f"{case['lang']:<6} {case['text']:<30} {'ERROR':<16} {str(e)[:28]:<30}")

    print("-" * 90)
    print(f"\n[BATCH] Results: {passed} passed, {failed} failed out of {len(test_cases)}")


# ============================================================
# HELPERS
# ============================================================
def print_result(input_text: str, parsed: dict, stt_time: float, llm_time: float):
    """Pretty print a single test result."""
    total = stt_time + llm_time

    print("\n┌─────────────────────────────────────────┐")
    print(f"│ Input:       {input_text}")
    print(f"│ English:     {parsed.get('english_translation', '?')}")
    print(f"│ Command:     {parsed.get('command', '?')}")
    print(f"│ Params:      {json.dumps(parsed.get('params', {}))}")
    print(f"│ Robot says:  \"{parsed.get('voice_response', '?')}\"")
    print(f"│ Timing:      STT {stt_time:.2f}s + LLM {llm_time:.2f}s = {total:.2f}s total")
    print("└─────────────────────────────────────────┘")


def print_summary(results: list):
    """Print summary of all test rounds."""
    if not results:
        print("No results recorded.")
        return

    print(f"\nTotal rounds: {len(results)}")

    for r in results:
        p = r["parsed"]
        stt = r.get("stt_time", 0)
        llm = r.get("llm_time", 0)
        print(f"  #{r['round']}: \"{r['input']}\" → {p['command']} ({stt + llm:.2f}s)")

    # Average timing
    avg_llm = sum(r.get("llm_time", 0) for r in results) / len(results)
    avg_stt = sum(r.get("stt_time", 0) for r in results) / len(results)
    print(f"\nAvg STT: {avg_stt:.2f}s | Avg LLM: {avg_llm:.2f}s | Avg Total: {avg_stt + avg_llm:.2f}s")


# ============================================================
# ENTRY POINT
# ============================================================
if __name__ == "__main__":
    if "--mock" in sys.argv:
        asyncio.run(test_mock_text())

    elif "--file" in sys.argv:
        idx = sys.argv.index("--file")
        if idx + 1 < len(sys.argv):
            asyncio.run(test_audio_file(sys.argv[idx + 1]))
        else:
            print("Usage: python test_speech_to_command.py --file <path-to-wav>")

    elif "--batch" in sys.argv:
        asyncio.run(run_batch_tests())

    else:
        asyncio.run(test_live_mic())
