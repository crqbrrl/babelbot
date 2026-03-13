"""
BabelBot - Test: Robot Command Execution
Tests every command in mock mode + validates LLM output → robot input.

3 test modes:
    1. MOCK ALL     → Run every command in mock mode, verify execution
    2. LLM → ROBOT  → Type voice text → LLM parses → mock robot executes
    3. LIVE ROBOT   → Same as mock but sends to real Cyberwave (use with caution)

Usage:
    python test_robot_commands.py                  # Mock all commands
    python test_robot_commands.py --llm            # Type text → LLM → mock robot
    python test_robot_commands.py --live            # Connect to real robot
    python test_robot_commands.py --sequence        # Run a demo sequence
"""

import sys
import json
import time
from robot import init_robot, execute, get_robot_status, _mock_execute
from llm import parse_command
from config import VALID_COMMANDS


# ============================================================
# TEST 1: Execute every command in mock mode
# ============================================================
def test_all_commands_mock():
    """
    Fire every valid command with default and custom params.
    No robot or API keys needed.
    """
    print("=" * 55)
    print("  TEST: All Robot Commands (Mock Mode)")
    print("=" * 55)

    test_cases = [
        # (command, params, expected behavior)
        ("move_forward", {}, "default distance"),
        ("move_forward", {"distance": 3.0}, "3 units forward"),
        ("move_backward", {}, "default distance"),
        ("move_backward", {"distance": 1.5}, "1.5 units backward"),
        ("turn_left", {}, "default 90 degrees"),
        ("turn_left", {"angle": 45}, "45 degrees"),
        ("turn_right", {}, "default 90 degrees"),
        ("turn_right", {"angle": 180}, "180 degrees"),
        ("sit", {}, "sit down"),
        ("stand", {}, "stand up"),
        ("wave", {}, "wave paw"),
        ("dance", {}, "dance"),
        ("shake_hand", {}, "shake hand"),
        ("stop", {}, "stop all"),
        # Edge cases
        ("move_forward", {"distance": 0}, "zero distance"),
        ("turn_left", {"angle": 360}, "full rotation"),
        ("unknown_command", {}, "should handle gracefully"),
    ]

    passed = 0
    failed = 0

    print(f"\n{'Command':<18} {'Params':<22} {'Result':<30} {'Status'}")
    print("-" * 80)

    for command, params, description in test_cases:
        try:
            result = _mock_execute(command, params)
            status = "OK"
            passed += 1
        except Exception as e:
            result = str(e)
            status = "FAIL"
            failed += 1

        params_str = json.dumps(params) if params else "{}"
        print(f"{command:<18} {params_str:<22} {result:<30} {status}")

    print("-" * 80)
    print(f"\nResults: {passed} passed, {failed} failed out of {len(test_cases)}")
    return failed == 0


# ============================================================
# TEST 2: LLM output → Robot input (full chain minus STT)
# ============================================================
def test_llm_to_robot():
    """
    Type a voice command in any language.
    LLM parses it → robot executes in mock mode.
    Tests the handoff between llm.py and robot.py.
    """
    print("=" * 55)
    print("  TEST: LLM → Robot (type commands in any language)")
    print("  Type 'quit' to exit, 'batch' for preset tests")
    print("=" * 55)

    results = []
    round_num = 0

    while True:
        try:
            text = input("\n[TYPE] Voice command: ").strip()

            if text.lower() in ("quit", "exit", "q"):
                break

            if text.lower() == "batch":
                run_batch_llm_to_robot()
                continue

            if not text:
                continue

            round_num += 1

            # Step 1: LLM parses
            t0 = time.time()
            parsed = parse_command(text)
            llm_time = time.time() - t0

            # Step 2: Robot executes
            t1 = time.time()
            result = execute(parsed["command"], parsed.get("params", {}))
            robot_time = time.time() - t1

            # Display
            print_chain_result(text, parsed, result, llm_time, robot_time)

            results.append({
                "round": round_num,
                "input": text,
                "command": parsed["command"],
                "result": result,
                "llm_time": llm_time,
            })

        except KeyboardInterrupt:
            break

    if results:
        print_chain_summary(results)


def run_batch_llm_to_robot():
    """
    Run preset multilingual commands through LLM → Robot.
    Validates the full chain works for each language.
    """
    test_cases = [
        # French
        ("FR", "Avance de deux pas"),
        ("FR", "Tourne a droite"),
        ("FR", "Assis"),
        ("FR", "Leve-toi"),
        ("FR", "Arrete-toi"),

        # Hindi
        ("HI", "आगे बढ़ो"),
        ("HI", "दाएं मुड़ो"),
        ("HI", "बैठ जाओ"),
        ("HI", "नाचो"),

        # German
        ("DE", "Geh vorwarts"),
        ("DE", "Dreh dich nach rechts"),
        ("DE", "Sitz"),
        ("DE", "Steh auf"),
        ("DE", "Gib Pfote"),

        # English
        ("EN", "Walk forward five steps"),
        ("EN", "Turn left 45 degrees"),
        ("EN", "Sit"),
        ("EN", "Dance for me"),
        ("EN", "Stop"),

        # Edge cases
        ("??", "asdfghjkl"),
        ("MIX", "Avance forward bitte"),
    ]

    print(f"\n[BATCH] Running {len(test_cases)} LLM → Robot tests...\n")
    print(f"{'Lang':<6} {'Input':<28} {'Command':<16} {'Params':<18} {'Robot Result':<22} {'Time'}")
    print("-" * 100)

    passed = 0
    failed = 0

    for lang, text in test_cases:
        try:
            t0 = time.time()
            parsed = parse_command(text)
            elapsed = time.time() - t0

            cmd = parsed.get("command", "???")
            params = parsed.get("params", {})

            # Execute on mock robot
            result = execute(cmd, params)

            is_valid = cmd in VALID_COMMANDS
            status = "OK" if is_valid else "FAIL"
            if is_valid:
                passed += 1
            else:
                failed += 1

            params_str = json.dumps(params)[:16]
            print(f"{lang:<6} {text:<28} {cmd:<16} {params_str:<18} {result[:20]:<22} {elapsed:.2f}s  {status}")

        except Exception as e:
            failed += 1
            print(f"{lang:<6} {text:<28} {'ERROR':<16} {'':<18} {str(e)[:20]:<22}")

    print("-" * 100)
    print(f"\n[BATCH] Results: {passed} passed, {failed} failed out of {len(test_cases)}")


# ============================================================
# TEST 3: Demo sequence (simulates a live demo)
# ============================================================
def test_demo_sequence():
    """
    Runs the exact sequence you'd do in the hackathon demo.
    3 people, 3 languages, 1 robot.
    """
    print("=" * 55)
    print("  TEST: Demo Sequence (simulates hackathon presentation)")
    print("=" * 55)

    demo_script = [
        {
            "speaker": "Cyriaque (FR)",
            "text": "Avance tout droit",
            "pause": 2,
        },
        {
            "speaker": "Cyriaque (FR)",
            "text": "Tourne a gauche",
            "pause": 2,
        },
        {
            "speaker": "Dev 1 (HI)",
            "text": "आगे बढ़ो तीन कदम",
            "pause": 2,
        },
        {
            "speaker": "Dev 1 (HI)",
            "text": "बैठ जाओ",
            "pause": 2,
        },
        {
            "speaker": "Dev 2 (DE)",
            "text": "Steh auf",
            "pause": 2,
        },
        {
            "speaker": "Dev 2 (DE)",
            "text": "Tanz fur uns",
            "pause": 2,
        },
        {
            "speaker": "All (EN)",
            "text": "Stop",
            "pause": 1,
        },
    ]

    print(f"\nRunning {len(demo_script)} demo steps...\n")

    for i, step in enumerate(demo_script, 1):
        print(f"\n{'='*50}")
        print(f"  Step {i}/{len(demo_script)}: {step['speaker']}")
        print(f"  Says: \"{step['text']}\"")
        print(f"{'='*50}")

        # Parse
        t0 = time.time()
        parsed = parse_command(step["text"])
        llm_time = time.time() - t0

        # Execute
        result = execute(parsed["command"], parsed.get("params", {}))

        # Display
        print(f"  Translation: {parsed.get('english_translation', '?')}")
        print(f"  Command:     {parsed['command']} {json.dumps(parsed.get('params', {}))}")
        print(f"  Robot:       {result}")
        print(f"  Voice:       \"{parsed.get('voice_response', '?')}\"")
        print(f"  Time:        {llm_time:.2f}s")

        # Pause between steps (simulating real demo timing)
        if i < len(demo_script):
            print(f"\n  [waiting {step['pause']}s before next step...]")
            time.sleep(step["pause"])

    print("\n" + "=" * 50)
    print("  DEMO SEQUENCE COMPLETE")
    print("=" * 50)


# ============================================================
# TEST 4: Live robot connection test
# ============================================================
def test_live_robot():
    """
    Actually connect to Cyberwave and test basic commands.
    Only use this when you have a real robot available.
    """
    print("=" * 55)
    print("  TEST: Live Robot Connection")
    print("  WARNING: This will send commands to the real robot!")
    print("=" * 55)

    # Try to connect
    connected = init_robot()
    status = get_robot_status()
    print(f"\nRobot status: {json.dumps(status, indent=2)}")

    if not connected:
        print("\n[FAIL] Could not connect to robot.")
        print("Check:")
        print("  1. CYBERWAVE_API_KEY is set")
        print("  2. CYBERWAVE_ENVIRONMENT_ID is set (if needed)")
        print("  3. Robot is powered on and connected")
        return

    print("\n[OK] Robot connected! Running safe test commands...\n")

    safe_commands = [
        ("stand", {}, "Stand up first"),
        ("move_forward", {"distance": 0.5}, "Small step forward"),
        ("stop", {}, "Stop"),
    ]

    for cmd, params, description in safe_commands:
        confirm = input(f"Execute '{cmd}' ({description})? [y/n]: ").strip().lower()
        if confirm == "y":
            result = execute(cmd, params)
            print(f"  Result: {result}\n")
        else:
            print("  Skipped.\n")

    print("[DONE] Live robot test complete.")


# ============================================================
# HELPERS
# ============================================================
def print_chain_result(input_text, parsed, robot_result, llm_time, robot_time):
    """Pretty print a full LLM → Robot chain result."""
    total = llm_time + robot_time

    print("\n┌─────────────────────────────────────────────┐")
    print(f"│ Voice input:    {input_text}")
    print(f"│ English:        {parsed.get('english_translation', '?')}")
    print(f"│ LLM command:    {parsed.get('command', '?')}")
    print(f"│ LLM params:     {json.dumps(parsed.get('params', {}))}")
    print(f"│ Robot result:   {robot_result}")
    print(f"│ Robot says:     \"{parsed.get('voice_response', '?')}\"")
    print(f"│ Timing:         LLM {llm_time:.2f}s + Robot {robot_time:.4f}s = {total:.2f}s")
    print("└─────────────────────────────────────────────┘")


def print_chain_summary(results):
    """Summary of LLM → Robot test session."""
    print("\n" + "=" * 50)
    print("  SESSION SUMMARY")
    print("=" * 50)
    print(f"Total commands: {len(results)}")

    for r in results:
        print(f"  #{r['round']}: \"{r['input']}\" → {r['command']} → {r['result']}")

    avg_time = sum(r["llm_time"] for r in results) / len(results)
    print(f"\nAvg LLM parse time: {avg_time:.2f}s")

    # Command distribution
    cmds = {}
    for r in results:
        cmds[r["command"]] = cmds.get(r["command"], 0) + 1
    print(f"Commands used: {json.dumps(cmds)}")


# ============================================================
# ENTRY POINT
# ============================================================
if __name__ == "__main__":
    if "--llm" in sys.argv:
        test_llm_to_robot()

    elif "--live" in sys.argv:
        test_live_robot()

    elif "--sequence" in sys.argv:
        test_demo_sequence()

    elif "--batch" in sys.argv:
        run_batch_llm_to_robot()

    else:
        test_all_commands_mock()
