import vonage

def get_ivr_client():
    ivr_client = vonage.Client(application_id="710b580c-b5f6-4d01-a6c2-6f0dfc4211ce", 
                                      private_key="secrets\private.key", max_retries=0)
    return ivr_client

## Change the url of the API
voice_answer_url = f"https://<your-ngrok_public_url-here>/webhooks/answer"
voice_event_url = f"https://<your-ngrok_public_url-here>/webhooks/events"

vonage_client = get_ivr_client()
call_payload = {
            "to": [{"type": "phone", "number": f"<number to call>"}],
            "from": {"type": "phone", "number": "+12014772880"},
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