import os

from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()

# Twilio credentials from environment variables
TWILIO_ACCOUNT_SID = os.environ.get("ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("AUTH_TOKEN")
TWILIO_PHONE = os.environ.get("FROM_NUMBER")
TO_PHONE = os.environ.get("TO_NUMBER")

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Use ngrok's public URL for TwiML instructions
ngrok_url = os.environ.get("NGROK_URL")  # Replace with your actual Ngrok URL

call = client.calls.create(
    url=f"{ngrok_url}/twiml",
    to=os.environ.get("TO_NUMBER"),
    from_=os.environ.get("FROM_NUMBER"),
)

print(call.sid)
