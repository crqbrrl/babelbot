"""
BabelBot - Text-to-Speech Module
Handles: English text → Smallest.ai Waves TTS → audio playback

The robot always responds in English regardless of input language.
"""

import os
import wave
import pyaudio
from smallestai.waves import WavesClient
from config import SMALLEST_API_KEY, TTS_VOICE_ID, TTS_MODEL, TTS_SPEED, CHUNK_SIZE


# Initialize Waves TTS client
tts_client = WavesClient(api_key=SMALLEST_API_KEY)

# Output directory for audio files
AUDIO_DIR = os.path.join(os.path.dirname(__file__), "audio_output")
os.makedirs(AUDIO_DIR, exist_ok=True)


def speak(text: str, play: bool = True) -> str:
    """
    Convert English text to speech and optionally play it.

    Args:
        text: English text to speak
        play: Whether to play through speakers (default True)

    Returns:
        Path to the generated WAV file
    """
    filepath = os.path.join(AUDIO_DIR, "response.wav")

    try:
        audio_bytes = tts_client.synthesize(
            text=text,
            voice_id=TTS_VOICE_ID,
            model=TTS_MODEL,
            speed=TTS_SPEED,
        )
        with open(filepath, "wb") as f:
            f.write(audio_bytes)
        print(f"[TTS] Generated: '{text}'")

        if play:
            play_audio(filepath)

        return filepath

    except Exception as e:
        print(f"[TTS] Error: {e}")
        # Fallback: just print it
        print(f"[TTS FALLBACK] Robot says: {text}")
        return ""


def play_audio(filepath: str):
    """
    Play a WAV file through the default speakers.

    Args:
        filepath: Path to WAV file
    """
    try:
        wf = wave.open(filepath, "rb")
        audio = pyaudio.PyAudio()

        stream = audio.open(
            format=audio.get_format_from_width(wf.getsampwidth()),
            channels=wf.getnchannels(),
            rate=wf.getframerate(),
            output=True,
        )

        data = wf.readframes(CHUNK_SIZE)
        while data:
            stream.write(data)
            data = wf.readframes(CHUNK_SIZE)

        stream.stop_stream()
        stream.close()
        audio.terminate()
        wf.close()
        print("[TTS] Playback complete")

    except Exception as e:
        print(f"[TTS] Playback error: {e}")


# ============================================================
# Quick test
# ============================================================
if __name__ == "__main__":
    print("Testing TTS module...")
    speak("Moving forward two steps")
    speak("Turning left")
    speak("Command received, sitting down now")
