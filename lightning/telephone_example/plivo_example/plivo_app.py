# FastAPI-based IVR application
import asyncio
import base64
import io
import json
import os
import time
import traceback
import urllib.parse

import requests
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Response, WebSocket, WebSocketDisconnect
from jinja2 import Environment, FileSystemLoader
from pydub import AudioSegment

xml_path = "../templates"  # Update with the correct path to XML templates
load_dotenv()

PLIVO_NGROK_URL = os.environ.get("NGROK_URL")

# Set up Jinja2 template environment
DEFAULT_TEMPLATE_ENVIRONMENT = Environment(loader=FileSystemLoader(xml_path))

# Initialize FastAPI app
app = FastAPI()
timeout = 1  # Timeout for receiving messages in seconds

# API authentication token
TOKEN = os.environ.get("SMALLEST_API_KEY")
EXTRA_HEADERS = {"origin": "https://smallest.ai"}
url = "http://waves-api.smallest.ai/api/v1/lightning/get_speech"

# Example payload for speech synthesis
with open("script.json", "r") as script_file:
    script_data = json.load(script_file)

payloads = [segment for segment in script_data["episode"]]

headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}


# Function to encode audio as WAV format
def encode_audio_common_wav(frame_input, sample_rate=8000, sample_width=2, channels=1):
    """Ensure the WAV file is encoded with standard settings"""
    audio = AudioSegment(
        data=frame_input,
        sample_width=sample_width,
        frame_rate=sample_rate,
        channels=channels,
    )
    wav_buf = io.BytesIO()
    audio.export(wav_buf, format="wav")
    wav_buf.seek(0)
    return wav_buf.read()


# Function to stream audio content asynchronously
async def waves_streaming(content, chunk_size=640):
    """Stream content in small chunks for Plivo streaming."""
    try:
        buffer = io.BytesIO(content)
        while True:
            chunk = buffer.read(chunk_size)
            if not chunk:
                break
            await asyncio.sleep(0.012)
            yield chunk
    except Exception as e:
        print(f"Exception occurred: {e}")
        traceback.print_exc()
        raise


# Render XML templates
def render_template(template_name: str, template_environment: Environment, **kwargs):
    template = template_environment.get_template(template_name)
    return template.render(**kwargs)


# Generate Plivo connection XML
def get_connection_plivoxml(call_id: str, base_url: str):
    return Response(
        render_template(
            template_name="plivo_connect_call_noid.xml",
            template_environment=DEFAULT_TEMPLATE_ENVIRONMENT,
            base_url=base_url,
            id=call_id,
        ),
        media_type="application/xml",
    )


# Webhook endpoint for inbound calls
@app.post("/inbound_call")
async def webhook(request: Request):
    xml_data = await request.body()
    parsed_data = urllib.parse.parse_qs(xml_data.decode("utf-8"))
    call_uuid = parsed_data.get("CallUUID", [None])[0]
    return get_connection_plivoxml(call_uuid, PLIVO_NGROK_URL.split("://")[1])


# WebSocket endpoint for call connection
@app.websocket("/connect_call")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            for payload in payloads:
                print(payload)
                data = json.loads(await ws.receive_text())
                if data["event"] == "start":
                    stream_id = data["start"]["streamId"]

                http_response = requests.post(url, json=payload, headers=headers)
                if http_response.status_code != 200:
                    print(f"Error: {http_response.status_code}")
                    return

                async for audio_chunk in waves_streaming(http_response.content):
                    if audio_chunk:
                        await ws.send_text(
                            json.dumps(
                                {
                                    "event": "playAudio",
                                    "media": {
                                        "payload": base64.b64encode(audio_chunk).decode(
                                            "utf-8"
                                        ),
                                        "sampleRate": 8000,
                                        "contentType": "audio/x-l16",
                                    },
                                }
                            )
                        )
                time.sleep(5)  # simulate gap between two payloads.
            break
    except WebSocketDisconnect:
        print("WebSocket disconnected")
    except Exception as e:
        print(f"Exception in WebSocket handler: {e}")
        traceback.print_exc()


# Run FastAPI application
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT")))
