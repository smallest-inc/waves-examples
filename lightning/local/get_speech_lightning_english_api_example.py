import requests
from datetime import datetime
import wave

TOKEN = "ENTER YOUR TOKEN HERE"

## Enter the URL
url = "http://waves-api.smallest.ai/api/v1/lightning/get_speech"
SAMPLE_RATE = 24000 ## Can be changed to 8000, 16000, 48000
VOICE_ID = "jessica"  ## Other Speakers: arman, james, emily 

## Edit the payload
payload = {
    "text": "Thank you for reaching out to us! We're here to assist you with any questions or concerns you may have.",
    "voice_id": VOICE_ID,
    "sample_rate": SAMPLE_RATE
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
    print(f"Saving the audio!! {response.status_code} {(datetime.now() - start_time).total_seconds()}")

    # Save the audio in bytes to a .wav file
    with wave.open('output_wav.wav', 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(SAMPLE_RATE)
        wav_file.writeframes(response.content)

    print("Audio file saved as output_wav.wav")
else:
    print(f"Error Occured with status code {response.status_code}")