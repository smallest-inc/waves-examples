import requests
from scipy.io import wavfile
import numpy as np
from datetime import datetime

TOKEN = "ENTER YOUR TOKEN HERE"

## Enter the URL
url = "http://waves-api.smallest.ai/api/v1/lightning/get_speech"
SAMPLE_RATE = 24000
## Edit the payload
payload = {
    "text": "रिमझिम बरसता सावन होगा",
    "voice_id": "raj",
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
print(f"Saving the audio!! {response.status_code} {(datetime.now() - start_time).total_seconds()}")

# Save the audio data as a WAV file using scipy
audio_data_from_bytes = np.frombuffer(response.content, dtype=np.int16)
wavfile.write('output_scipy.wav', SAMPLE_RATE, audio_data_from_bytes)


    
