import json
import vonage

with open('config.json', 'r', encoding='utf-8') as f:
    config_data = json.load(f)

def get_ivr_client():
    ivr_client = vonage.Client(application_id=config_data['vonage_application_id'], 
                                      private_key="secrets/private.key", max_retries=0)
    return ivr_client

## Change the url of the API
voice_answer_url = f"https://{config_data['ngrok_url']}/webhooks/answer"
voice_event_url = f"https://{config_data['ngrok_url']}/webhooks/events"

vonage_client = get_ivr_client()
call_payload = {
            "to": [{"type": "phone", "number": f"{config_data['customer_number_to_call']}"}],
            "from": {"type": "phone", "number": f"{config_data['vonage_number']}"},
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