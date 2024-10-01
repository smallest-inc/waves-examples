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

app = FastAPI()

TIMEOUT = 2  # Timeout in seconds for receiving a message
CLOSE_CONNECTION_TIMEOUT = 500  # Timeout for your websocket connection

with open('config.json', 'r', encoding='utf-8') as f:
    config_data = json.load(f)

url = f"wss://call-dev.smallest.ai/invocations_streaming?token={config_data['waves_token']}"

### Supporting functions

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


async def waves_streaming(url: str, payload: list):
    """Awaaz streaming demo function.

    Args:
        url (str): URL
        payloads (list): List of dictionaries of payloads that are sent to API.

    Returns:
        bytes: Audio bytes generated for the sentences concatenated together.
    """
    first = False
    wav_audio_bytes = b""
    print(f"Start_time: {datetime.now(timezone.utc)}")
    start_time = time.time()

    try:
        async with websockets.connect(url) as websocket:
            first = False
            connected_time = datetime.now(timezone.utc)
            print(f"Connected_time: {datetime.now(timezone.utc)}")
            data = json.dumps(payload)
            await websocket.send(data)

            # Collect responses until no more data or timeout
            response = b""
            while True:
                response_part = await asyncio.wait_for(websocket.recv(),
                                                        timeout=TIMEOUT)
                if response_part == "<START>":
                    print("Connection started, Now you will get superfast speeds")
                elif response_part == "<END>":
                    print("End of response received")
                    print(f"last response time: {datetime.now(timezone.utc)}")
                else:
                    response += response_part
                    print(f"Responses are being read: {datetime.now(timezone.utc)}")
                    if not first:
                        print(f"time to first byte: {(datetime.now(timezone.utc) - connected_time).total_seconds()}")
                        print(f"First response: {datetime.now(timezone.utc)}")
                        first = True
                    yield response_part

            # Handle the accumulated response if needed
            wav_audio_bytes += response

            # Optionally close the connection if needed
            if (time.time() - start_time) > CLOSE_CONNECTION_TIMEOUT:
                await websocket.close()

    except websockets.exceptions.ConnectionClosed as e:
        if e.code == 1000:
            print("Connection closed normally (code 1000).")
        else:
            print(f"Connection closed with code {e.code}: {e.reason}")
    except Exception as e:
        print(f"Exception occurred: {e}")

    finally:
        print(f"Connection closed: {datetime.now(timezone.utc)}")


### API routes for calling 
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
        for idx, payload in enumerate(config_data['payloads']):
            
            call_start_time = datetime.now()
            prev_time = call_start_time
            current_time = call_start_time
            tmp_audio_buffer = AudioBuffer(b'')
            
            # send the chunks to socket on each chunk from the API
            async for audio_chunk in waves_streaming(url, payload):
                if audio_chunk:
                    
                    # For each chunk - add the chunk to a audio buffer
                    tmp_audio_buffer.extend(AudioBuffer(audio_chunk))

                    # Keep popping from the audio buffer until empty
                    while len(tmp_audio_buffer) > 0:
                        current_time = datetime.now()
                        if len(tmp_audio_buffer):
                            ai_speaking_count = 0
                            if (current_time - prev_time).total_seconds() >= 0.012:
                                tmp_audio_chunk = tmp_audio_buffer.pop_chunk()
                                if not tmp_audio_chunk or len(tmp_audio_chunk) != 640:
                                    if tmp_audio_chunk:
                                        print(f"sending weird: {len(tmp_audio_chunk)}")
                                        ai_speaking_count += 1
                                else:
                                    await ws.send_bytes(tmp_audio_chunk)
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