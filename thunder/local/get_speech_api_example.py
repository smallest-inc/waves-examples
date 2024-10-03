import requests

## Enter the URL
url = "https://api.smallest.ai/awaaz/get_speech"

TOKEN = "ENTER YOUR TOKEN HERE"

## Edit the payload
payload = {
    "text": "भारत एक विशाल देश है, जिसमें विभिन्न भाषाएँ संस्कृतियाँ और परंपराएँ समाहित हैं। ",
    "voice_id": "amar_indian_male",
    "speed": 1.2,
    "add_wav_header": True,
    "sample_rate": 24000
}

## Edit the header - enter Token
headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

## Send the reponse and save the audio
print("Sending the request!!")
response = requests.request("POST", url, json=payload, headers=headers)
print("Saving the audio!!")
with open("waves_demo.wav", "wb") as f:
    f.write(bytes(response.content))

    
