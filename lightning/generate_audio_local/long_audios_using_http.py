################## Environment setup #######################
# 1. conda setup
#     - conda create -n waves_venv python=3.10 -y
#     - conda activate waves_venv
#     - pip install websockets pydub
    
# 2. pipenv setup
#     - python -m venv waves_venv
#     - pip install websockets pydub
############################################################


# import asyncio
import io
import json
import time
from datetime import datetime, timezone
import requests
import io

# import websockets
from pydub import AudioSegment

###################### Do your changes here ###########################

TOKEN = "YOUR_TOKEN_HERE"  # Your token ID
SAMPLE_RATE = 24000  # Sample rate of the audio that you wish to generate
SPEED = 1.0  # Speed of the audio that you wish to generate
MODEL = "lightning" #Choose from either one of - 1. lightning 2. thunder
TIMEOUT = 2  # Timeout in seconds for receiving a message
CLOSE_CONNECTION_TIMEOUT = 500  # Timeout for your websocket connection
URL = "https://waves-api.smallest.ai/api/v1/lightning/get_speech"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

INPUTS = [
    ("We at smallest build ultra-realistic, high speed voice models tailored for realtime applications.", "emily"),
    ("हम highly detailed, fast-paced voice models बनाते हैं जो real-time situations में use करने के लिए designed हैं।", "mithali")
]

############## Do not change anything below this ######################

SAMPLE_WIDTH = 2
CHANNELS = 1

def fetch_audio(sentence, voice_id):
    """Fetch audio for a given sentence and voice ID using the REST API.

    Args:
        sentence (str): Text to convert to speech.
        voice_id (str): Voice ID for TTS.

    Returns:
        bytes: Audio bytes for the given sentence.
    """
    payload = {
        "text": sentence,
        "voice_id": voice_id,
        "sample_rate": SAMPLE_RATE,
        "speed": SPEED,
        "transliterate":False
    }
    
    start_time = time.time()
    response = requests.request("POST", URL, json=payload, headers=HEADERS)
    
    if response.status_code == 200:
        latency = (time.time() - start_time) * 1000  # Convert to ms
        print(f"Audio received! Status: {response.status_code}, Latency: {int(latency)} ms")
        return response.content
    else:
        print(f"Error occurred: Status {response.status_code}, Message: {response.text}")
        return b""


def concatenate_audio(sentences_voices):
    """Concatenate audio data for all sentences and voices.

    Args:
        sentences_voices (dict): Dictionary mapping sentences to voice IDs.

    Returns:
        bytes: Concatenated audio bytes.
    """
    concatenated_audio = AudioSegment.silent(duration=0)
    
    for sentence, voice_id in sentences_voices:
        audio_data = fetch_audio(sentence, voice_id)
        if audio_data:
            audio_segment = AudioSegment(data=audio_data, sample_width=SAMPLE_WIDTH, frame_rate=SAMPLE_RATE, channels=CHANNELS)
            concatenated_audio += audio_segment
    
    return concatenated_audio.raw_data


def save_audio_file(audio_data, filename="waves_demo_streaming.wav"):
    """Save concatenated audio data to a WAV file with headers.

    Args:
        audio_data (bytes): Concatenated audio data.
        filename (str): Name of the output file.
    """
    audio_data_with_header = add_wav_header(audio_data, sample_rate=SAMPLE_RATE)
    with open(filename, "wb") as f:
        f.write(audio_data_with_header)
    print(f"Audio file saved as {filename} at {datetime.now(timezone.utc)}")


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


def main():
    concatenated_audio_data = concatenate_audio(INPUTS)
    if concatenated_audio_data:
        save_audio_file(concatenated_audio_data)
    else:
        print("No audio data to save.")

if __name__ == "__main__":
    main()
