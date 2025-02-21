import os
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

# Twilio credentials from environment variables
TWILIO_ACCOUNT_SID=os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN=os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_PHONE=os.environ.get("TWILIO_PHONE")

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Use ngrok's public URL for TwiML instructions
ngrok_url = "https://4410-35-240-215-206.ngrok-free.app/twiml"  # Replace with your actual Ngrok URL

call = client.calls.create(
    url=ngrok_url,  
    to="+919723946908",
    from_="+18287528082",
)

call = client.calls.create(
    url=ngrok_url,  
    to=os.environ.get("TWILIO_TO_PHONE"),
    from_=os.environ.get("TWILIO_PHONE"),
)

print(call.sid)
