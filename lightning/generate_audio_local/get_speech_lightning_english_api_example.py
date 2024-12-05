import requests
from datetime import datetime
import wave

TOKEN = "YOUR_TOKEN_HERE"

## Enter the URL
url = "https://waves-api.smallest.ai/api/v1/lightning/get_speech"
SAMPLE_RATE = 24000 ## Can be changed to 8000, 16000, 48000
VOICE_ID = "emily"  ## List of supported voices can be found here: https://waves-docs.smallest.ai/waves-api

## Edit the payload
payload = {
    "text": "We at smallest build ultra-realistic, high speed voice models tailored for realtime applications, achieving hyper realistic audio generation.",
    "voice_id": VOICE_ID,
    "sample_rate": SAMPLE_RATE,
    "speed": 1.0,
    "language": "en",
    "add_wav_header": True,
    "transliterate": False,
    "remove_extra_silence": False
}

## Edit the header - enter Token
headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

## Send the reponse and save the audio
print(f"Sending the request!! {datetime.now()}")
start_time = datetime.now()
response = requests.request("POST", url, json=payload, headers=headers)

if response.status_code == 200:
    print(f"Saving the audio!! {response.status_code} Latency: {(datetime.now() - start_time).total_seconds()}")

    # Save the audio in bytes to a .wav file
    with open('waves_lightning_sample_audio_en.wav', 'wb') as wav_file:
        wav_file.write(response.content)

    print("Audio file saved as waves_lightning_sample_audio.wav")
else:
    print(f"Error Occured with status code {response.status_code}")