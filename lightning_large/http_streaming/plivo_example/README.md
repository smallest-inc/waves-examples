# Smallest.ai Streaming API Example with Phonetic Call

This guide demonstrates how to use the **Smallest.ai Streaming API** with phonetic call functionality. It sets up a local FastAPI server that streams audio data and uses `ngrok` to expose the server for public testing. Both **Vonage** and **Plivo** are supported.

## Prerequisites

Ensure you have the following installed:

- **Python 3.7+**
- **ngrok** ([Download here](https://ngrok.com/download)) - used to expose localhost to the internet.

## General Steps

1. **Install the required dependencies:**
   - Run the following command to install the necessary Python packages:
     ```bash
     pip install -r requirements.txt
     ```

2. **Set up ngrok:**
   - Install `ngrok`, then run the command to expose your FastAPI server:
     ```bash
     ngrok http 5001 # Use this port for all apps
     ```

3. **Get the ngrok public URL:**
   - In the ngrok terminal, a public URL will be displayed, e.g., `https://abcd-1234-5678.ngrok.io`.

4. **Config:**
  - Change `.env` and replace with your keys, secrets and ngrok url.

5. **Script:**
  - Change `script.json` and change the text and voice_id as per need.

6. **Run the FastAPI application in a new terminal:**
   - For each provider - go to their respective folder and run 
     ```bash
     python plivo_app.py
     ```

7. **Run the phonetic call client in a new terminal: (Update the phone numbers, ngrok URL and path in the config.yaml first!)**
   - For each provider - go to their respective folder and run 
     ```bash
     python plivo_make_call.py
     ```

---

**Note:** If you have a public URL for your application, ngrok is not required.

This setup allows seamless phonetic call testing using both Vonage, Plivo and Twilio platforms.