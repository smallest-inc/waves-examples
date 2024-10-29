################## Environment setup #######################
# 1. conda setup
#     - conda create -n waves_venv python=3.10 -y
#     - conda activate waves_venv
#     - pip install websockets pydub
    
# 2. pipenv setup
#     - python -m venv waves_venv
#     - pip install websockets pydub
############################################################

import asyncio
import io
import json
import time
from datetime import datetime, timezone

import websockets
from pydub import AudioSegment

###################### Do your changes here ###########################

TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiaGFtZWVzQHNtYWxsZXN0LmFpIn0.v55OTV0EMB2tALid-cqiV49UzhDRg_tMKT-19PKavY0"  # Your token ID
SAMPLE_RATE = 24000  # Sample rate of the audio that you wish to generate
SPEED = 1.0  # Speed of the audio that you wish to generate
MODEL = "lightning" #Choose from either one of - 1. lightning 2. thunder
VOICE_ID = "mithali"  # List of supported voices can be found here: https://waves-docs.smallest.ai/waves-api
TIMEOUT = 2  # Timeout in seconds for receiving a message
CLOSE_CONNECTION_TIMEOUT = 500  # Timeout for your websocket connection
SENTENCES = ["  ", "हम highly detailed, fast-paced voice models बनाते हैं जो real-time situations में use करने के लिए designed हैं। ये models बहुत ज़्यादा realistic sound produce कर सकते हैं।"]
WAVES_STREAMING_URL = f"wss://waves-api.smallest.ai/api/v1/{MODEL}/get_streaming_speech?token={TOKEN}"
EXTRA_HEADERS = {"origin": "https://smallest.ai"}

############## Do not change anything below this ######################

SAMPLE_WIDTH = 2
CHANNELS = 1

def add_wav_header(frame_input, sample_rate=24000, sample_width=2, channels=1):
    """Ensure the WAV file is encoded with standard settings.

    Args:
        frame_input (bytes): Audio bytes.
        sample_rate (int, optional): Sample rate needed. Defaults to 24000.
        sample_width (int, optional): Sample width of audio. Defaults to 2.
        channels (int, optional): Channels of the audio. Defaults to 1.

    Returns:
        bytes: Audio data with proper header.
    """
    audio = AudioSegment(data=frame_input, sample_width=sample_width, frame_rate=sample_rate, channels=channels)
    wav_buf = io.BytesIO()
    audio.export(wav_buf, format="wav")
    wav_buf.seek(0)
    return wav_buf.read()


waves_websocket_url = WAVES_STREAMING_URL
waves_payloads = []

for sentence in SENTENCES:
    payload = {
        "text": sentence,
        "voice_id": VOICE_ID,
        "add_wav_header": False,
        "language": "hi",
        "sample_rate": SAMPLE_RATE,
        "speed": SPEED,
        "keep_ws_open": True,
        "remove_extra_silence": True, 
        "transliterate": True,
        "get_end_of_response_token": True
    }
    waves_payloads.append(payload)


async def waves_streaming(url: str, payloads: list):
    """waves streaming demo function.

    Args:
        url (str): URL
        payload (list): A dictionary representing the payload to send to the API.

    Returns:
        bytes: Audio bytes generated for the sentences concatenated together.
    """
    wav_audio_bytes = b""
    print(f"Start_time: {datetime.now(timezone.utc)}")
    start_time = time.time()
    first = True

    try:
        async with websockets.connect(url, extra_headers=EXTRA_HEADERS) as websocket:
            # Convert payload to JSON and record the time before sending
            for payload in payloads:
                data = json.dumps(payload)
                await websocket.send(data)
                payload_start_time = time.time()

                # Collect responses until no more data or timeout
                response = b""
                while True:
                    response_part = await asyncio.wait_for(websocket.recv(), timeout=TIMEOUT)

                    # Check for special markers in the response
                    if response_part == "<START>":
                        print("Connection started, Now you will get superfast speeds")
                        break
                    elif response_part == "<END>":
                        last_response_time = time.time()
                        total_latency = (last_response_time - payload_start_time) * 1000  # Convert to ms
                        print(f"Time to last byte: {int(total_latency)} ms")
                        break
                    else:
                        # Accumulate the response parts
                        response += response_part
                        if first:
                            first_response_time = time.time()
                            latency = (first_response_time - payload_start_time) * 1000  # Convert to ms
                            print(f"Time to first byte: {int(latency)} ms")
                            first = False

            # Append the accumulated response to wav_audio_bytes
            wav_audio_bytes += response

            # Check if connection timeout has been reached
            if (time.time() - start_time) > CLOSE_CONNECTION_TIMEOUT:
                await websocket.close()
                print("Connection closed due to timeout.")

    except websockets.exceptions.ConnectionClosed as e:
        if e.code == 1000:
            print("Connection closed normally (code 1000).")
        else:
            print(f"Connection closed with code {e.code}: {e.reason}")
        return None
    except Exception as e:
        print(f"Exception occurred: {e}")

    finally:
        print(f"Connection closed: {datetime.now(timezone.utc)}")
        return wav_audio_bytes


async def post_process(audio_data):
    """Post-process the provided audio data by ensuring the total length of the WAV audio bytes
    aligns with the required sample width and number of channels.

    Args:
        audio_data (bytes): The audio data in WAV format that needs to be processed.

    Returns:
        bytes: Audio bytes with post processing
    """
    total_length = len(audio_data)
    alignment = SAMPLE_WIDTH * CHANNELS
    padding_length = (alignment - (total_length % alignment)) % alignment
    audio_data += b"\x00" * padding_length
    return audio_data


# Example usage with async event loop
async def main():
    """Main function to generate, post-process, and save audio data as a WAV file."""
    # Generate audio data
    wav_audio_bytes = await waves_streaming(waves_websocket_url, waves_payloads)
    if wav_audio_bytes is None:
        print("Some error occured, Did you check your token?")
    else:
        ################ Optional Post processing for saving the file ###################
        wav_audio_bytes = await post_process(wav_audio_bytes)
        #################################################################################
    
        # Use audio_data as needed
        print(f"Saving audio file: {datetime.now(timezone.utc)}")
        wav_audio_bytes = add_wav_header(wav_audio_bytes, sample_rate=SAMPLE_RATE)
        with open("waves_demo.wav", "wb") as f:
            f.write(wav_audio_bytes)

if __name__ == "__main__":
    asyncio.run(main())
