import plivo
import os
from dotenv import load_dotenv

load_dotenv()
NGROK_PUBLIC_URL = "https://your_ngrok_url.ngrok.io" ## Add your ngrok URL here

def get_ivr_client():
    ivr_client = plivo.RestClient(auth_id=os.environ.get("PLIVO_AUTH_ID"), auth_token=os.environ.get("PLIVO_AUTH_TOKEN"))
    return ivr_client

plivo_client = get_ivr_client()
call_payload = {
    "to": f"<your number here>",  # Recipient phone number
    "from": f"+912231043567"   # Caller phone number
}

def make_a_call():
    print("making a call")
    try:
        call_response = plivo_client.calls.create(
            from_=call_payload['from'], 
            to_=call_payload['to'], 
            answer_url=f"{NGROK_PUBLIC_URL}/inbound_call",
            answer_method="POST"
        )
        if call_response:
            print("Call started:", call_response)
        else:
            print("Call failed")
    except BaseException as e:
        print(f"Error {str(e)}")
    return call_response

make_a_call()