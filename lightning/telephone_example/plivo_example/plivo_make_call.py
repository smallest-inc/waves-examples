import plivo  # Plivo SDK for making voice calls
import os
from dotenv import load_dotenv  # Load environment variables from .env file

# Load environment variables from .env file
load_dotenv()

# Set your Ngrok public URL to handle incoming call responses
NGROK_PUBLIC_URL = "https://4410-35-240-215-206.ngrok-free.app"  # Replace with your actual Ngrok URL

def get_ivr_client():
    """
    Initialize and return the Plivo REST client using authentication credentials.
    """
    ivr_client = plivo.RestClient(
        auth_id=os.environ.get("PLIVO_AUTH_ID"),  # Fetch Plivo Auth ID from environment variables
        auth_token=os.environ.get("PLIVO_AUTH_TOKEN")  # Fetch Plivo Auth Token from environment variables
    )
    return ivr_client

# Initialize the Plivo REST client
plivo_client = get_ivr_client()
call_payload = {
    "to": os.environ.get("PLIVO_TO_NUMBER"),  # Recipient phone number
    "from": os.environ.get("PLIVO_FROM_NUMBER")   # Caller phone number
}

def make_a_call():
    """
    Initiates an outbound call using the Plivo API.
    """
    print("Making a call...")
    try:
        # Create an outbound call
        call_response = plivo_client.calls.create(
            from_=call_payload['from'],  # Caller ID
            to_=call_payload['to'],  # Recipient phone number
            answer_url=f"{NGROK_PUBLIC_URL}/inbound_call",  # URL to handle the call response
            answer_method="POST"  # HTTP method to request the answer URL
        )
        
        # Check if the call response is received
        if call_response:
            print("Call started successfully:", call_response)
        else:
            print("Call failed")
    except BaseException as e:
        # Print the error if the call fails
        print(f"Error: {str(e)}")
    
    return call_response  # Return the response for further processing if needed

# Initiate the call
make_a_call()
