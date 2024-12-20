import traceback
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import JSONResponse
import asyncio
import json
import time
from datetime import datetime, timezone
from audio import AudioBuffer
import websockets
from pydub import AudioSegment
import io
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

timeout = 1  # Timeout in seconds for receiving a message
CLOSE_CONNECTION_TIMEOUT = 500  # Timeout for a single connection set at 600 seconds.

# Add your token here
TOKEN = os.environ.get("SMALLEST_API_KEY")
EXTRA_HEADERS = {"origin": "https://smallest.ai"}
url = f"wss://waves-api.smallest.ai/api/v1/lightning/get_streaming_speech?token={TOKEN}"

# Payloads for streaming API
payloads = [
    {
        'text': 'smallest एआई में आपका स्वागत है। आज मैं आपकी कैसे सहायता कर सकता हूँ?', 
        'voice_id': 'raj', 
        'add_wav_header': False, 
        'language': 'hi', 
        'sample_rate': 16000, 
        'speed': 1.0, 
        'keep_ws_open': True, 
        'remove_extra_silence': False,
        'transliterate': True,
        'get_end_of_response_token': True
    },
]

def encode_audio_common_wav(frame_input, sample_rate=16000, sample_width=2, channels=1):
    """Ensure the WAV file is encoded with standard settings"""
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


async def waves_streaming(url, payload):
    """
        url: URL to streaming smallest.ai Api
        payload: Payload for the Api
    """
    wav_audio_bytes = b''
    
    try:
        async with websockets.connect(url, extra_headers=EXTRA_HEADERS) as websocket:
            print(f"connected_time: {datetime.now(timezone.utc)}")
            data = json.dumps(payload)
            await websocket.send(data)

            while True:
                try:
                    response_part = await asyncio.wait_for(websocket.recv(), timeout=timeout)
                    if response_part:
                        wav_audio_bytes += response_part
                        yield response_part
                    else:
                        break
                except asyncio.TimeoutError:
                    print("Timeout while waiting for response")
                    break

            
    except websockets.exceptions.ConnectionClosed as e:
        if e.code == 1000:
            print("Connection closed normally (code 1000).")
        else:
            print(f"Connection closed with code {e.code}: {e.reason}")
    except Exception as e:
        print(f"Exception occurred: {e}")
        traceback.print_exc()
    finally:
        print("Connection closed")


@app.get("/webhooks/answer")
async def answer_call(request: Request):
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
    return "200"

@app.websocket("/socket")
async def websocket_endpoint(ws:WebSocket):
    await ws.accept()
    
    try:
        # For each payload
        for idx, payload in enumerate(payloads):
            call_start_time = datetime.now()
            prev_time = call_start_time
            current_time = call_start_time
            tmp_audio_buffer = AudioBuffer(b'')
            response = b''
            # send the chunks to socket on each chunk from the API
            async for audio_chunk in waves_streaming(url, payload):
                if audio_chunk:
                    tmp_audio_buffer.extend(AudioBuffer(audio_chunk))

                    while len(tmp_audio_buffer) > 0:
                        current_time = datetime.now()

                        if len(tmp_audio_buffer):
                            ai_speaking_count = 0
                            if (current_time - prev_time).total_seconds() >= 0.012:
                                x = tmp_audio_buffer.pop_chunk()
                                response += x

                                if not x or len(x) != 640:
                                    if x:
                                        ai_speaking_count += 1
                                else:
                                    await ws.send_bytes(x)
                                prev_time = current_time
                        else:
                            print("Chunk Completed")
                                        
    except WebSocketDisconnect:
        print("WebSocket disconnected")
    except Exception as e:
        print(f"Exception occurred in WebSocket handler: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=8000, ws_ping_timeout=600)