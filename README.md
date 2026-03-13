# BabelBot — Multilingual Voice-to-Robot Controller

3 people. 3 languages. 1 robot dog that understands them all.

Speak French, Hindi, German, or English — the Unitree Go2 robot dog obeys every command and confirms in English.

Built at the [Robotic Agents Hackathon](https://luma.com/robotic-agents-hackathon) (SF, March 2026).

## Architecture

```
[Voice FR/HI/DE/EN]
    → Smallest.ai Pulse STT (multilingual transcription)
    → Ollama gpt-oss:20b (translate + extract robot command as JSON)
    → Cyberwave SDK (Unitree Go2 robot dog moves)
    → Smallest.ai Waves TTS (English voice confirmation)
```

## Project Structure

```
babelbot/
├── config.py                   # API keys, constants, robot commands
├── stt.py                      # Mic → Smallest.ai Pulse STT → text
├── llm.py                      # Text (any language) → LLM → command JSON
├── robot.py                    # Command → Cyberwave SDK → Unitree Go2
├── tts.py                      # English text → Smallest.ai Waves → speaker
├── main.py                     # Main loop (voice or test mode)
├── test_speech_to_command.py   # Test: STT → LLM pipeline
├── test_robot_commands.py      # Test: LLM → Robot pipeline
├── requirements.txt
└── setup.sh
```

## Quick Start

```bash
# 1. Install
chmod +x setup.sh && ./setup.sh

# 2. Set API keys
export SMALLEST_API_KEY="your-key"
# Ollama runs locally — ensure `ollama serve` is running with model gpt-oss:20b
export CYBERWAVE_API_KEY="your-key"

# 3. Run
python main.py          # Full voice mode (mic required)
python main.py --test   # Test mode (type commands)
```

## Testing

```bash
# Test LLM parsing only (no mic needed, only Ollama)
python test_speech_to_command.py --mock

# Batch test all languages (23 preset commands)
python test_speech_to_command.py --batch

# Test all robot commands in mock mode (no API keys needed)
python test_robot_commands.py

# Test LLM → Robot chain (type commands)
python test_robot_commands.py --llm

# Run the hackathon demo sequence
python test_robot_commands.py --sequence

# Test with real robot (sends actual commands)
python test_robot_commands.py --live
```

## Team

- **Cyriaque** — Product, demo, pitch (French voice)
- **Dev 1** — Robot integration via Cyberwave (Hindi voice)
- **Dev 2** — STT/TTS pipeline via Smallest.ai (German voice)

## Tech Stack

- [Cyberwave Python SDK](https://github.com/cyberwave-os/cyberwave-python) — Robot control
- [Smallest.ai Python SDK](https://github.com/smallest-inc/smallest-python-sdk) — STT + TTS
- [Ollama](https://ollama.com/) — Command parsing (gpt-oss:20b, local)
- [Unitree Go2](https://www.unitree.com/go2/) — Robot dog hardware

## Hackathon Tracks

Eligible for: Cyberwave, Smallest.ai, ElevenLabs, Toolhouse, Scrapegraph, Featherless
