import plivo

def get_ivr_client():
    ivr_client = plivo.RestClient(auth_id="<your auth id>", auth_token="<your auth token>")
    return ivr_client

plivo_client = get_ivr_client()
call_payload = {
    "to": f"<your phone number>",  # Recipient phone number
    "from": f"+912231043567"   # Caller phone number
}

def make_a_call():
    print("making a call")
    try:
        call_response = plivo_client.calls.create(
            from_=call_payload['from'], 
            to_=call_payload['to'], 
            answer_url="<ngrok url>/inbound_call",
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
