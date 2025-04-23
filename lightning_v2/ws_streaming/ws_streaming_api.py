#!/usr/bin/env python3
import time
import json
import base64
import wave
from websocket import WebSocketApp

# =========== CONFIG ===========
WS_URL = "wss://waves-api.smallest.ai/api/v1/lightning-v2/get_speech/stream"
TOKEN = "<TEXT>"
HEADERS = {
    "Authorization": (
        f"Bearer {TOKEN}"
    )
}
VOICE_ID    = "<VOICE>"
SAMPLE_TEXT = "<TEXT>"
OUTPUT_PATH = "output.wav"
SAMPLE_RATE = 24000
SPEED      = 1.0
CONSISTENCY = 0.5
ENHANCEMENT = 1
SIMILARITY   = 0
LANGUAGE = "en"

def save_wav(chunks, path, sample_rate=24000):
    """Decode base64 chunks and write a WAV file."""
    pcm_data = b"".join(base64.b64decode(c) for c in chunks)
    with wave.open(path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)          # 16-bit samples
        wf.setframerate(sample_rate)
        wf.writeframes(pcm_data)
    print(f"✔ Saved audio to: {path}")

def tts_and_save(text, voice_id, output_path):
    audio_chunks = []
    start_time     = None
    ttfb_ms        = None

    def on_open(ws):
        nonlocal start_time
        payload = {
                "voice_id": voice_id, 
                "text": text, 
                "language": LANGUAGE,
                "sample_rate": SAMPLE_RATE, 
                "speed": SPEED, 
                "consistency": CONSISTENCY, 
                "similarity": SIMILARITY,
                "enhancement": ENHANCEMENT
            }
        
        start_time = time.time()
        ws.send(json.dumps(payload))
        print("⏳ Request sent...")

    def on_message(ws, message):
        nonlocal ttfb_ms
        data = json.loads(message)
        audio_b64 = data.get("data", {}).get("audio")

        # measure TTFB on first chunk
        if audio_b64 and ttfb_ms is None:
            ttfb_ms = (time.time() - start_time) * 1000
            print(f"🚀 Time to first byte: {ttfb_ms:.1f} ms")

        if audio_b64:
            audio_chunks.append(audio_b64)

        # close once complete
        status = data.get("status") or data.get("payload", {}).get("status")
        if status == "complete":
            ws.close()

    def on_error(ws, error):
        print("❌ WebSocket error:", error)
        ws.close()

    def on_close(ws, *args):
        total_ms = (time.time() - start_time) * 1000
        print(f"⏱ Total request time: {total_ms:.1f} ms")

        if audio_chunks:
            save_wav(audio_chunks, output_path, sample_rate=SAMPLE_RATE)
        else:
            print("⚠️ No audio received.")

    ws = WebSocketApp(
        WS_URL,
        header=[f"{k}: {v}" for k, v in HEADERS.items()],
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws.run_forever()

if __name__ == "__main__":
    tts_and_save(SAMPLE_TEXT, VOICE_ID, OUTPUT_PATH)
