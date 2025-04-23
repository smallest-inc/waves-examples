import base64
import io
import json
import time

import requests
from pydub import AudioSegment

url = "https://waves-api.smallest.ai/api/v1/lightning-large/stream"

def encode_audio_common_wav(frame_input, sample_rate=24000, sample_width=2, channels=1):
    """
    Encodes raw audio data into a WAV file format with standard settings.

    Args:
        frame_input (bytes): The raw audio data to be encoded.
        sample_rate (int, optional): The sample rate of the audio in Hz. Defaults to 24000.
        sample_width (int, optional): The sample width in bytes. Defaults to 2.
        channels (int, optional): The number of audio channels. Defaults to 1.

    Returns:
        bytes: The encoded audio data in WAV file format.
    """
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

def stream(payload, headers):
    """
    Streams audio data from a server using an HTTP POST request and writes the received audio to a WAV file.
    Args:
        payload (dict): The JSON payload to send in the POST request. Must include a "sample_rate" key.
        headers (dict): The headers to include in the POST request.
    Raises:
        requests.RequestException: If the HTTP request fails.
        Exception: For any other unexpected errors.
    Notes:
        - The function calculates and prints the Time to First Byte (TTFB) in milliseconds.
        - The response is expected to be a server-sent event (SSE) stream where each line contains JSON data.
        - The JSON data must include a base64-encoded "audio" field for audio chunks.
        - The audio chunks are decoded, written to a WAV file, and stored in memory for size calculations.
        - A WAV header is generated and written to the file before the audio chunks.
    Output:
        - A file named "output.wav" containing the streamed audio data.
        - Prints the total number of audio chunks and their combined size in bytes.
    """
    try:
        start = time.time()
        response = requests.post(url, json=payload, headers=headers, stream=True)
        print(f"TTFB: {1000 * (time.time() - start):.2f} ms")
        response.raise_for_status()
        
        with open("output.wav", "wb") as f:
            audio_chunks = []
            wavHeader=encode_audio_common_wav(b"", sample_rate=payload["sample_rate"], sample_width=2, channels=1)
            f.write(wavHeader)
            for i, line in enumerate(response.iter_lines()):
                try:
                    chunk = line.decode('utf-8')
                    if chunk.startswith("data: "):
                        data = json.loads(chunk[6:])
                        if "audio" in data:
                            audio_data = base64.b64decode(data["audio"])
                            audio_chunks.append(audio_data)
                            f.write(audio_data)
                except json.JSONDecodeError as je:
                    print(f"JSON Decode Error: {je}")
                except Exception as e:
                    print(f"Error processing chunk: {e}")
            
            print(f"Total audio chunks: {len(audio_chunks)}")
            print(f"Total audio size: {sum(len(chunk) for chunk in audio_chunks)} bytes")

    except requests.RequestException as e:
        print(f"Request failed: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    payload = {
        "text": "<TEXT>",
        "voice_id": "<VOICE>",
        "sample_rate": 24000,
        "speed": 1,
        "language": "en",
        "consistency": 0.5,
        "similarity": 0,
        "enhancement": 1,
    }

    headers = {
        "Authorization": "Bearer <AUTH TOKEN>",
        "Content-Type": "application/json"
    }

    stream(payload, headers)