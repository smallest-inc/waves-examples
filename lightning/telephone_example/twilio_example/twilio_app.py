from fastapi import FastAPI, WebSocket, Request, Response
from fastapi.templating import Jinja2Templates
import json
import base64
import asyncio
import traceback
import io
import os
from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader
import urllib.parse
import audioop
import aiohttp
from fastapi import WebSocket, WebSocketDisconnect

# Load environment variables from .env file
load_dotenv()

# Configuration for Jinja2 template rendering
xml_path = "templates"
DEFAULT_TEMPLATE_ENVIRONMENT = Environment(
    loader=FileSystemLoader(xml_path)
)

# Ngrok URL for public exposure of local server
NGROK_URL = "https://4410-35-240-215-206.ngrok-free.app"  # Update with your ngrok URL

# Initialize FastAPI application and template rendering
app = FastAPI()
templates = Jinja2Templates(directory=xml_path)

# Waves API Configuration
TOKEN = os.environ.get("SMALLEST_API_KEY")  # Fetch API key from environment variables
url = f"http://waves-api.smallest.ai/api/v1/lightning/get_speech"  # TTS API endpoint

# Predefined TTS payload
payloads = [
    {
        'text': 'smallest एआई में आपका स्वागत है। आज मैं आपकी कैसे सहायता कर सकता हूँ?', 
        'voice_id': 'pragya', 
        'add_wav_header': False, 
        'sample_rate': 8000, 
        'speed': 1.0,
    }
]

# Headers for API requests
headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

async def waves_streaming(content: bytes, chunk_size: int = 640):
    """Streams audio content in chunks."""
    try:
        buffer = io.BytesIO(content)
        while True:
            chunk = buffer.read(chunk_size)
            if not chunk:
                break
            yield chunk  # Yield each chunk for processing
    except Exception as e:
        print(f"Streaming error: {e}")
        traceback.print_exc()
        raise

def render_template(template_name: str, template_environment: Environment, **kwargs):
    """Renders XML templates using Jinja2."""
    template = template_environment.get_template(template_name)
    return template.render(**kwargs)

def get_connection_twilioxml(
    base_url: str,
    call_sid: str,  # CallSid is required for Twilio WebSocket connection
    template_environment: Environment = DEFAULT_TEMPLATE_ENVIRONMENT,
):
    """Returns XML response with WebSocket connection URL."""
    print(f"wss://{base_url}/stream/{call_sid}")  # Print WebSocket URL for debugging
    return Response(
        render_template(
            template_name="twilio_streams.xml",
            template_environment=template_environment,
            base_url=f"wss://{base_url}/stream/{call_sid}",  # Insert CallSid in URL
        ),
        media_type="application/xml",
    )

@app.post("/twiml")
async def twiml_endpoint(request: Request):
    """Handles incoming requests from Twilio and returns TwiML response."""
    try:
        body = await request.body()
        decoded_data = body.decode('utf-8')
        parsed_data = urllib.parse.parse_qs(decoded_data)
        
        # Extract CallSid from parsed request data
        call_sid = parsed_data.get('CallSid', [''])[0]
        print(f"CallSid: {call_sid}")

        # Extract base URL from ngrok URL
        base_url = NGROK_URL.split("://")[1]
        return get_connection_twilioxml(base_url, call_sid)
    except Exception as e:
        print(f"Error in twiml_endpoint: {e}")
        traceback.print_exc()
        return Response(
            '<?xml version="1.0" encoding="UTF-8"?><Response></Response>',
            media_type="application/xml"
        )

@app.websocket("/stream/{call_sid}")
async def websocket_endpoint(ws: WebSocket, call_sid: str):
    """Handles WebSocket connection for streaming audio."""
    await ws.accept()
    print(f"Twilio WebSocket connection accepted for call {call_sid}")    
    
    connection_active = True  # Track connection state

    try:
        while connection_active:
            try:
                data = await ws.receive_text()
                event_data = json.loads(data)  # Parse incoming WebSocket message
            except WebSocketDisconnect:
                print(f"WebSocket disconnected for call {call_sid}")
                connection_active = False
                break
            except Exception as e:
                print(f"Error receiving WebSocket data: {e}")
                connection_active = False
                break
            
            if event_data['event'] == 'start':
                print(f"Streaming started for call {call_sid}")
                continue
                
            stream_id = event_data.get('streamSid')
            if not stream_id:
                continue
                
            for payload in payloads:
                if not connection_active:
                    break
                    
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.post(url, json=payload, headers=headers) as response:
                            if response.status != 200:
                                print(f"Error occurred with status code {response.status}")
                                continue
                                
                            tts_audio = await response.read()
                            if isinstance(tts_audio, bytes):
                                tts_audio = audioop.lin2ulaw(tts_audio, 2)  # Convert audio format
                                
                            async for chunk in waves_streaming(tts_audio):
                                if not connection_active:
                                    break
                                    
                                if not chunk:
                                    continue
                                    
                                try:
                                    payload = base64.b64encode(chunk).decode("utf-8")  # Encode audio chunk
                                    await ws.send_text(json.dumps({
                                        "event": "media",
                                        "streamSid": stream_id,
                                        "media": {
                                            "payload": payload
                                        }
                                    }))
                                    
                                    await asyncio.sleep(0.03)  # Small delay to simulate real-time streaming
                                except WebSocketDisconnect:
                                    print(f"WebSocket disconnected during streaming for call {call_sid}")
                                    connection_active = False
                                    break
                                except Exception as e:
                                    print(f"Error sending WebSocket data: {e}")
                                    connection_active = False
                                    break
                            
                    if connection_active:
                        print("Chunk completed")
                
                except Exception as e:
                    print(f"Error in HTTP request: {e}")
                    continue
            break    
    except WebSocketDisconnect:
        print(f"WebSocket disconnected for call {call_sid}")
    except Exception as e:
        print(f"WebSocket error for call {call_sid}: {e}")
        traceback.print_exc()
    finally:
        if not ws.client_state.DISCONNECTED:
            await ws.close()
        print(f"WebSocket connection closed for call {call_sid}")

if __name__ == "__main__":
    import uvicorn
    # Run FastAPI server
    uvicorn.run(app, host="0.0.0.0", port=5000)