import vonage
import os
from dotenv import load_dotenv

load_dotenv()

NGROK_PUBLIC_URL = "https://4410-35-240-215-206.ngrok-free.app" ## Add your ngrok URL here

def get_ivr_client():
    ivr_client = vonage.Client(application_id=os.environ.get("VONAGE_APPLICATION_ID"), 
                                      private_key="secrets/private.key", max_retries=0) # change the private key path
    return ivr_client

vonage_client = get_ivr_client()
## Change the url of the API
voice_answer_url = f"{NGROK_PUBLIC_URL}/webhooks/answer"
voice_event_url = f"{NGROK_PUBLIC_URL}/webhooks/events"

call_payload = {
            "to": [{"type": "phone", "number": os.environ.get("VONAGE_TO_PHONE")}],
            "from": {"type": "phone", "number": os.environ.get("VONAGE_PHONE")},
            "answer_url": [voice_answer_url],
            "event_url": [voice_event_url]
        }

def make_a_call():
    print("making a call")
    try:
        call_response = vonage_client.voice.create_call(call_payload)
        if call_response["status"] == "started":
            print("Call started")
        else:
            print("failed")

    except BaseException as e:
        print(f"Error {str(e)}")
    return call_response

make_a_call()