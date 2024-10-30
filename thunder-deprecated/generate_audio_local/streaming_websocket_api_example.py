################## Environment setup #######################
# 1. conda setup
#     - conda create -n awaaz_venv python=3.10 -y
#     - conda activate awaaz_venv
#     - pip install websockets pydub
    
# 2. pipenv setup
#     - python -m venv awaaz_venv
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

TOKEN = "Enter your token here"  # Your token ID
SAMPLE_RATE = 24000  # Sample rate of the audio that you wish to generate
SPEED = 1.3  # Speed of the audio that you wish to generate
VOICE_ID = "saaira_indian_female"  # Voice id that you wish to use
TIMEOUT = 2  # Timeout in seconds for receiving a message
CLOSE_CONNECTION_TIMEOUT = 500  # Timeout for your websocket connection
SENTENCES = ["  ", "भारत एक विशाल देश है, ","जिसमें विभिन्न भाषाएँ संस्कृतियाँ ", "और परंपराएँ समाहित हैं। ", " "]

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


awaaz_websocket_url = f"wss://call-dev.smallest.ai/invocations_streaming?token={TOKEN}"
awaaz_payloads = []
for sentence in SENTENCES:
    payload = {
        "text": sentence,
        "voice_id": VOICE_ID,
        "add_wav_header": False,
        "language": "hi",
        "sample_rate": SAMPLE_RATE,
        "speed": SPEED,
        "keep_ws_open": True,
        "remove_extra_silence": False,
        "transliterate": False,
        "get_end_of_response_token": True
    }
    awaaz_payloads.append(payload)


async def waves_streaming(url: str, payloads: list):
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
             for payload in payloads:
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
                        break
                    elif response_part == "<END>":
                        print("End of response received")
                        print(f"last response time: {datetime.now(timezone.utc)}")
                        break
                    else:
                        response += response_part
                        print(f"Responses are being read: {datetime.now(timezone.utc)}")
                        if not first:
                            print(f"time to first byte: {(datetime.now(timezone.utc) - connected_time).total_seconds()}")
                            print(f"First response: {datetime.now(timezone.utc)}")
                            first = True

                # Handle the accumulated response if needed
                wav_audio_bytes += response
                time.sleep(1)

                # Optionally close the connection if needed
                if (time.time() - start_time) > CLOSE_CONNECTION_TIMEOUT:
                    await websocket.close()
                    break  # Exit the loop if the connection is closed

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
    wav_audio_bytes = await waves_streaming(awaaz_websocket_url, awaaz_payloads)
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
