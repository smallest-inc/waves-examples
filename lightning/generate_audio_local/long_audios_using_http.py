import io
import json
import time
import argparse
from datetime import datetime, timezone
import requests
from pydub import AudioSegment
import re

# Configuration constants
TOKEN = "your_token_here"  # Replace with your token ID
SAMPLE_RATE = 24000  # Sample rate of the audio that you wish to generate
SPEED = 1.0  # Speed of the audio that you wish to generate
MODEL = "lightning"  # Choose from either one of - 1. lightning 2. thunder
TIMEOUT = 2  # Timeout in seconds for receiving a message
CLOSE_CONNECTION_TIMEOUT = 500  # Timeout for your websocket connection
URL = "https://waves-api.smallest.ai/api/v1/lightning/get_speech"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

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
        "transliterate": False
    }
    
    start_time = time.time()
    response = requests.post(URL, json=payload, headers=HEADERS)
    
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
        sentences_voices (list): List of tuples containing sentence and voice ID.

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

def split_paragraph_into_sentences(paragraph, min_length=10):
    # Regular expression to match sentences (ending with .!?)
    sentence_endings = r'(?<=[.!?]) +'
    sentences = re.split(sentence_endings, paragraph.strip())
    
    # Join short sentences with the next one until they reach the minimum length
    result = []
    current_sentence = ""
    
    for sentence in sentences:
        if len(current_sentence) + len(sentence) < min_length:
            current_sentence += " " + sentence
        else:
            if current_sentence:
                result.append(current_sentence.strip())
            current_sentence = sentence
    
    # Add the last sentence
    if current_sentence:
        result.append(current_sentence.strip())
    
    return result


def load_input_data(json_file):
    """Load the input data (sentences and voice IDs) from a JSON file.

    Args:
        json_file (str): Path to the JSON file containing sentences and voice IDs.

    Returns:
        list: List of tuples containing sentence and voice ID.
    """
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    all_sentences = []

    for ele in data:
        sentence = ele['sentence']
        voice_id = ele['voice_id']

        split_sentences = split_paragraph_into_sentences(sentence)
        
        sentences_voices = [(sen, voice_id) for sen in split_sentences]
    
        all_sentences.extend(sentences_voices)
    print(all_sentences)
    return all_sentences

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Generate and save speech from text.")
    parser.add_argument(
        "json_file", 
        nargs="?",  # Makes the argument optional
        default="input_data.json",  # Default to input_data.json if no argument is provided
        help="Path to the JSON file containing sentences and voice IDs (default: input_data.json)."
    )
    args = parser.parse_args()

    # Load input data from JSON file
    sentences_voices = load_input_data(args.json_file)
    
    # Concatenate audio and save the file
    concatenated_audio_data = concatenate_audio(sentences_voices)
    if concatenated_audio_data:
        save_audio_file(concatenated_audio_data)
    else:
        print("No audio data to save.")

if __name__ == "__main__":
    main()
