"""
BabelBot - Speech-to-Text Module
Handles: mic recording → Smallest.ai Pulse STT → text
Supports: French, Hindi, German, English (multilingual)
"""

import json
import asyncio
import wave
import io
import sounddevice as sd
import aiohttp
import websockets
from config import (
    SMALLEST_API_KEY,
    STT_WS_URL,
    STT_REST_URL,
    SAMPLE_RATE,
    CHANNELS,
    CHUNK_SIZE,
    RECORD_SECONDS,
)


def record_from_mic(duration: int = RECORD_SECONDS) -> bytes:
    """
    Record audio from the microphone using sounddevice (PipeWire-compatible).

    Args:
        duration: How many seconds to record (default from config)

    Returns:
        Raw audio bytes (PCM 16-bit)
    """
    import numpy as np

    print(f"[MIC] Listening for {duration}s... Speak now!")

    recording = sd.rec(
        int(SAMPLE_RATE * duration),
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype="int16",
    )
    sd.wait()

    raw_audio = recording.tobytes()
    print(f"[MIC] Recorded {len(raw_audio)} bytes")
    return raw_audio


def raw_to_wav(raw_audio: bytes) -> bytes:
    """Convert raw PCM bytes to WAV format for the REST API."""
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(2)  # 16-bit = 2 bytes
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(raw_audio)
    return buffer.getvalue()


async def transcribe_streaming(raw_audio: bytes) -> str:
    """
    Stream audio to Smallest.ai Pulse STT via WebSocket.
    This is the fast path (64ms latency).

    Args:
        raw_audio: PCM 16-bit audio bytes

    Returns:
        Transcribed text (any language)
    """
    headers = {
        "Authorization": f"Bearer {SMALLEST_API_KEY}",
    }

    try:
        return await asyncio.wait_for(_transcribe_ws(raw_audio, headers), timeout=10)
    except Exception as e:
        print(f"[STT] WebSocket error: {e}, falling back to REST API")
        return await transcribe_rest(raw_audio)


async def _transcribe_ws(raw_audio: bytes, headers: dict) -> str:
    """Internal WebSocket transcription with no timeout (caller handles it)."""
    async with websockets.connect(STT_WS_URL, additional_headers=headers) as ws:
        # Send configuration
        config = {
            "type": "config",
            "sample_rate": SAMPLE_RATE,
            "language": "multi",  # multilingual mode
        }
        await ws.send(json.dumps(config))

        # Stream audio in chunks
        chunk_size = 4096
        for i in range(0, len(raw_audio), chunk_size):
            chunk = raw_audio[i:i + chunk_size]
            await ws.send(chunk)
            await asyncio.sleep(0.01)  # small delay to avoid overwhelming

        # Signal end of audio
        await ws.send(json.dumps({"type": "end"}))

        # Collect transcript
        full_text = ""
        async for message in ws:
            data = json.loads(message)
            if data.get("type") == "transcript":
                full_text = data.get("text", "")
                print(f"[STT partial] {full_text}")
            elif data.get("type") == "final":
                if data.get("text"):
                    full_text = data["text"]
                break

        print(f"[STT] Final: {full_text}")
        return full_text


async def transcribe_rest(raw_audio: bytes) -> str:
    """
    Fallback: Send audio to Pulse STT via REST API.
    Slightly slower but more reliable.

    Args:
        raw_audio: PCM 16-bit audio bytes

    Returns:
        Transcribed text
    """
    wav_audio = raw_to_wav(raw_audio)
    headers = {
        "Authorization": f"Bearer {SMALLEST_API_KEY}",
    }

    timeout = aiohttp.ClientTimeout(total=10)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        data = aiohttp.FormData()
        data.add_field(
            "file",
            wav_audio,
            filename="recording.wav",
            content_type="audio/wav",
        )
        data.add_field("language", "multi")

        async with session.post(STT_REST_URL, headers=headers, data=data) as resp:
            if resp.status == 200:
                result = await resp.json()
                text = result.get("text", "")
                print(f"[STT REST] {text}")
                return text
            else:
                error = await resp.text()
                print(f"[STT REST] Error {resp.status}: {error}")
                return ""


async def listen_and_transcribe(duration: int = RECORD_SECONDS) -> str:
    """
    Full pipeline: record from mic → transcribe.
    This is the main function your app calls.

    Args:
        duration: Recording duration in seconds

    Returns:
        Transcribed text in the original language
    """
    raw_audio = record_from_mic(duration)
    text = await transcribe_streaming(raw_audio)
    return text


# ============================================================
# Quick test
# ============================================================
if __name__ == "__main__":
    print("Testing STT module...")
    result = asyncio.run(listen_and_transcribe(5))
    print(f"You said: {result}")
