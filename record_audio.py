"""
BabelBot - Record audio clips locally
Record your voice in your language and save as WAV files.
Share these with teammates so everyone can test without a mic.

Usage:
    python record_audio.py                     # Record one clip (5s)
    python record_audio.py --duration 10       # Record for 10 seconds
    python record_audio.py --name french_test  # Custom filename
    python record_audio.py --batch             # Record multiple clips in a row
"""

import sys
import os
import wave
import pyaudio
from config import SAMPLE_RATE, CHANNELS, CHUNK_SIZE

# Where audio clips are saved
CLIPS_DIR = os.path.join(os.path.dirname(__file__), "audio_clips")
os.makedirs(CLIPS_DIR, exist_ok=True)


def record_clip(duration: int = 5, filename: str = None) -> str:
    """
    Record audio from mic and save as WAV.

    Args:
        duration: Seconds to record
        filename: Custom name (without .wav extension)

    Returns:
        Path to saved WAV file
    """
    if filename is None:
        # Auto-name: clip_001.wav, clip_002.wav, etc.
        existing = [f for f in os.listdir(CLIPS_DIR) if f.endswith(".wav")]
        num = len(existing) + 1
        filename = f"clip_{num:03d}"

    filepath = os.path.join(CLIPS_DIR, f"{filename}.wav")

    audio = pyaudio.PyAudio()
    stream = audio.open(
        format=pyaudio.paInt16,
        channels=CHANNELS,
        rate=SAMPLE_RATE,
        input=True,
        frames_per_buffer=CHUNK_SIZE,
    )

    print(f"[REC] Recording for {duration}s... Speak now!")
    print(f"[REC] Say your command in your language")

    frames = []
    for _ in range(0, int(SAMPLE_RATE / CHUNK_SIZE * duration)):
        data = stream.read(CHUNK_SIZE, exception_on_overflow=False)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    audio.terminate()

    # Save as WAV
    with wave.open(filepath, "wb") as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(b"".join(frames))

    size_kb = os.path.getsize(filepath) / 1024
    print(f"[REC] Saved: {filepath} ({size_kb:.0f} KB)")
    return filepath


def batch_record():
    """
    Record multiple clips in a row.
    Press Enter to start each recording, 'q' to stop.
    """
    print("=" * 50)
    print("  Batch Recording Mode")
    print("  Press Enter to record, 'q' to quit")
    print("=" * 50)

    clip_num = 0
    clips = []

    while True:
        clip_num += 1
        name = input(f"\n[Clip {clip_num}] Name (or Enter for auto, 'q' to quit): ").strip()

        if name.lower() == "q":
            break

        duration = 5
        dur_input = input(f"[Clip {clip_num}] Duration in seconds (default 5): ").strip()
        if dur_input.isdigit():
            duration = int(dur_input)

        filepath = record_clip(
            duration=duration,
            filename=name if name else None,
        )
        clips.append(filepath)

    print(f"\n[DONE] Recorded {len(clips)} clips:")
    for c in clips:
        print(f"  {c}")

    print(f"\nAll clips saved in: {CLIPS_DIR}")
    print(f"Share this folder with teammates or test with:")
    print(f"  python test_speech_to_command.py --file <path-to-wav>")


if __name__ == "__main__":
    if "--batch" in sys.argv:
        batch_record()
    else:
        # Parse args
        duration = 5
        name = None

        if "--duration" in sys.argv:
            idx = sys.argv.index("--duration")
            if idx + 1 < len(sys.argv):
                duration = int(sys.argv[idx + 1])

        if "--name" in sys.argv:
            idx = sys.argv.index("--name")
            if idx + 1 < len(sys.argv):
                name = sys.argv[idx + 1]

        filepath = record_clip(duration=duration, filename=name)

        print(f"\nTo test this clip through the full pipeline:")
        print(f"  python test_speech_to_command.py --file {filepath}")
