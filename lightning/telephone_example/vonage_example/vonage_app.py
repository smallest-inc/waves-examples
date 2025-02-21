import traceback
from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import JSONResponse
import asyncio
import json
import time
from datetime import datetime, timezone
from audio import AudioBuffer  # Custom audio buffering utility
from pydub import AudioSegment
import io
from dotenv import load_dotenv
import aiohttp
import os

# Load environment variables
load_dotenv()

app = FastAPI()

# Timeout configurations
TIMEOUT = 1  # Timeout in seconds for receiving a message
CLOSE_CONNECTION_TIMEOUT = 500  # Maximum connection duration in seconds

# Fetch API key from environment variables
TOKEN = os.environ.get("SMALLEST_API_KEY")
EXTRA_HEADERS = {"origin": "https://smallest.ai"}
url = "http://waves-api.smallest.ai/api/v1/lightning/get_speech"

print(url)  # Print API endpoint for debugging

# Define TTS request payload
payloads = [
    {
        'text': 'smallest एआई में आपका स्वागत है। आज मैं आपकी कैसे सहायता कर सकता हूँ?', 
        'voice_id': 'pragya', 
        'add_wav_header': False, 
        'sample_rate': 16000, 
        'speed': 1.0, 
    }
]

# HTTP headers for API request
headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def encode_audio_common_wav(frame_input, sample_rate=16000, sample_width=2, channels=1):
    """
    Encodes audio into a WAV format with standard settings.
    Args:
        frame_input: Raw audio data.
        sample_rate: Audio sample rate (default: 16kHz).
        sample_width: Bit depth (default: 2 bytes per sample).
        channels: Number of audio channels (default: mono).
    Returns:
        WAV-encoded byte stream.
    """
    audio = AudioSegment(
        data=frame_input,
        sample_width=sample_width,
        frame_rate=sample_rate,
        channels=channels
    )
    
    wav_buf = io.BytesIO()
    audio.export(wav_buf, format="wav")
    wav_buf.seek(0)
    return wav_buf.read()

async def waves_streaming(content, chunk_size=640):
    """
    Generator function to stream audio in chunks.
    Args:
        content: Binary audio content from API response.
        chunk_size: Number of bytes per chunk (default: 640 bytes).
    """
    try:
        buffer = io.BytesIO(content)
        while True:
            chunk = buffer.read(chunk_size)
            if not chunk:
                break
            yield chunk
    except Exception as e:
        print(f"Exception occurred: {e}")
        traceback.print_exc()
        raise

@app.get("/webhooks/answer")
async def answer_call(request: Request):
    """
    Handles incoming call webhook by returning NCCO response to connect via WebSocket.
    """
    host_header = request.headers.get('host', 'localhost')
    ncco = [
        {
            "action": "connect",
            "from": "Vonage",
            "endpoint": [
                {
                    "type": "websocket",
                    "uri": f"wss://{host_header}/socket",
                    "content-type": "audio/l16;rate=16000",
                    "headers": {
                        "uuid": request.query_params.get("uuid")
                    }
                }
            ],
        },
    ]
    return JSONResponse(ncco)

@app.post("/webhooks/events")
async def events():
    """Handles event webhooks (placeholder endpoint)."""
    return "200"

@app.websocket("/socket")
async def websocket_endpoint(ws: WebSocket):
    """
    WebSocket handler for receiving and sending audio data.
    """
    await ws.accept()
    print("Vonage WebSocket connection accepted")

    try:
        # Receive initial WebSocket message
        data = await ws.receive_text()
        event_data = json.loads(data)
        
        # Process each TTS payload
        for idx, payload in enumerate(payloads):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, json=payload, headers=headers) as response:
                        if response.status != 200:
                            print(f"Error occurred with status code {response.status}")
                            continue
                        
                        tts_audio = await response.read()  # Fetch synthesized speech data
                        
                        call_start_time = datetime.now()
                        prev_time = call_start_time
                        current_time = call_start_time
                        tmp_audio_buffer = AudioBuffer(b'')  # Buffer for streaming audio
                        accumulated_audio = b''
                        
                        async for audio_chunk in waves_streaming(tts_audio):   
                            if not audio_chunk:
                                continue
                            
                            await ws.send_bytes(audio_chunk)  # Send chunk to WebSocket

                            await asyncio.sleep(0.02)  # Ensure minimum sleep to avoid rapid exhaustion
                
                print(f"Chunk {idx + 1} completed")
                            
            except Exception as e:
                print(f"Error processing chunk {idx}: {e}")
                continue
                
    except Exception as e:
        print(f"Exception occurred in WebSocket handler: {e}")
        traceback.print_exc()
    finally:
        try:
            await ws.close()
        except:
            pass
        print("WebSocket connection closed")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=5000, ws_ping_timeout=600)
