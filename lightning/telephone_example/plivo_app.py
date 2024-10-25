from fastapi import FastAPI, Request, WebSocket, Response
from fastapi.responses import PlainTextResponse
from jinja2 import Environment, FileSystemLoader
import urllib.parse
import json
import base64
import time
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


xml_path = r"waves-core\examples\phonetic_calling\templates"

DEFAULT_TEMPLATE_ENVIRONMENT = Environment(
    loader=FileSystemLoader(xml_path)
)

app = FastAPI()

timeout = 1  # Timeout in seconds for receiving a message

url = 'wss://smallest-ai.meeshogcp.in/get_streaming_speech?token=<your-token-here>'

# Payloads for streaming API
payloads = [
    {'text': 'Aap apne order ko cancel kar sakte hain.', 'voice_id': 'aravind', 'language': 'hi', 'speed': 1.1, 'remove_extra_silence': True, 'sample_rate': 8000, 'add_wav_header': False, 'keep_ws_open': True, 'transliterate': True, 'get_end_of_response_token': False},
    {'text': 'Lekin aapka order cash on delivery hai,', 'voice_id': 'aravind', 'language': 'hi', 'speed': 1.1, 'remove_extra_silence': True, 'sample_rate': 8000, 'add_wav_header': False, 'keep_ws_open': True, 'transliterate': True, 'get_end_of_response_token': False},
    {'text': 'Agar aapka order prepaid hota,', 'voice_id': 'aravind', 'language': 'hi', 'speed': 1.1, 'remove_extra_silence': True, 'sample_rate': 8000, 'add_wav_header': False, 'keep_ws_open': True, 'transliterate': True, 'get_end_of_response_token': False},
    {'text': 'to aapko refund milta. Aur aapka order cash on delivery hai,', 'voice_id': 'aravind', 'language': 'hi', 'speed': 1.1, 'remove_extra_silence': True, 'sample_rate': 8000, 'add_wav_header': False, 'keep_ws_open': True, 'transliterate': True, 'get_end_of_response_token': False},
    {'text': 'toh ismein koi paise nahi lagenge.', 'voice_id': 'aravind', 'language': 'hi', 'speed': 1.1, 'remove_extra_silence': True, 'sample_rate': 8000, 'add_wav_header': False, 'keep_ws_open': True, 'transliterate': True, 'get_end_of_response_token': False},
    {'text': ' ', 'voice_id': 'aravind', 'language': 'hi', 'speed': 1.1, 'remove_extra_silence': True, 'sample_rate': 8000, 'add_wav_header': False, 'keep_ws_open': True, 'transliterate': True, 'get_end_of_response_token': True}
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


async def awaaz_streaming(url, payload):
    """
        url: URL to streaming smallest.ai Api
        payload: Payload for the Api
    """
    wav_audio_bytes = b''
    print(f"start_time: {datetime.now(timezone.utc)}")
    start_time = time.time()
    
    try:
        async with websockets.connect(url) as websocket:
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

            # print(f"Time elapsed since connection is open: {time.time() - start_time}")
            # print(f"Assume now that the other processes run - user speaks and llm responds")
            # # await asyncio.sleep(5)
            
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

def render_template(template_name: str, template_environment: Environment, **kwargs):
    template = template_environment.get_template(template_name)
    return template.render(**kwargs)

def get_connection_plivoxml(
    call_id: str,
    base_url: str,
    template_environment: Environment = DEFAULT_TEMPLATE_ENVIRONMENT,
):
    return Response(
        render_template(
            template_name="plivo_connect_call_noid.xml",
            template_environment=template_environment,
            base_url=base_url,
            id=call_id,
        ),
        media_type="application/xml",
    )

# POST webhook endpoint that reads and returns XML
@app.post("/inbound_call")
async def webhook(request: Request):
    xml_data = await request.body()
    decoded_data = xml_data.decode('utf-8')

    # Parse the URL-encoded string into a dictionary
    parsed_data = urllib.parse.parse_qs(decoded_data)

    # Extract the CallUUID
    call_uuid = parsed_data.get('CallUUID', [None])[0]    
    
    return get_connection_plivoxml(call_uuid, "1b23-2406-7400-56-6aea-8cd4-8424-a054-4458.ngrok-free.app")

# WebSocket endpoint
@app.websocket("/connect_call")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()

    try:
        # For each payload
        for idx, payload in enumerate(payloads):
            data = await ws.receive_text()
            print(data)
            data = json.loads(data)
            if data['event'] == 'start':
                stream_id = data['start']['streamId']

            call_start_time = datetime.now()
            prev_time = call_start_time
            current_time = call_start_time
            tmp_audio_buffer = AudioBuffer(b'')
            response = b''
            # send the chunks to socket on each chunk from the API
            async for audio_chunk in awaaz_streaming(url, payload):
                if audio_chunk:
                    tmp_audio_buffer.extend(AudioBuffer(audio_chunk))
                    print("Len of Audio Chunk is: ", len(audio_chunk))
                    while len(tmp_audio_buffer) > 0:
                        current_time = datetime.now()

                        if len(tmp_audio_buffer):
                            ai_speaking_count = 0
                            if (current_time - prev_time).total_seconds() >= 0.012:
                                x = tmp_audio_buffer.pop_chunk()
                                response += x

                                print("Length of Chunk x is: ", len(x))
                                print("length of total audio is: ", len(tmp_audio_buffer))
                                # print("x is: ", x)
                                if not x or len(x) != 640:
                                    if x:
                                        print(f"sending weird: {len(x)}")
                                        ai_speaking_count += 1
                                else:
                                    payload = base64.b64encode(x).decode("utf-8")

                                    data = {
                                        'event': 'playAudio',
                                        # 'streamSid': self.stream_sid,
                                        'media': {
                                            'payload': payload,
                                            'sampleRate': 8000, 
                                            'contentType': 'audio/x-l16'
                                        }
                                    }    
                                    # time.sleep(1)
                                    await ws.send_text(json.dumps(data))  # Echo the received message back to the client

                                    mark_message = {
                                        "event": "checkpoint",
                                        "streamId": stream_id,
                                        "name": "random"
                                    }
                                    print("mark sent")
                                    await ws.send_text(json.dumps(mark_message))

                                    # await ws.send_bytes(x)
                                    print("X is sent")
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
    uvicorn.run(app, host="0.0.0.0", port=5000)