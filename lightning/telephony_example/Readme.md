# Smallest.ai Streaming API Example with Phonetic Call

This guide demonstrates how to use the **Smallest.ai Streaming API** with phonetic call functionality. It sets up a local FastAPI server that streams audio data and uses `ngrok` to expose the server for public testing. Both **Vonage** and **Plivo** are supported.

## Prerequisites

Ensure you have the following installed:

- **Python 3.7+**
- **ngrok** ([Download here](https://ngrok.com/download)) - used to expose localhost to the internet.

## General Steps

1. **Set up ngrok:**
   - Install `ngrok`, then run the command to expose your FastAPI server:
     ```bash
     ngrok http 8000  # For Vonage
     ngrok http 5000  # For Plivo
     ```

2. **Install the required dependencies:**
   - Run the following command to install the necessary Python packages:
     ```bash
     pip install -r requirements.txt
     ```

3. **Run the FastAPI application:**
   - For Vonage:
     ```bash
     python app.py
     ```
   - For Plivo (add the required token in the script):
     ```bash
     python plivo_app.py
     ```

4. **Get the ngrok public URL:**
   - In the ngrok terminal, a public URL will be displayed, e.g., `https://abcd-1234-5678.ngrok.io`.

5. **Run the phonetic call client:**
   - For Vonage:
     ```bash
     python make_call.py
     ```
   - For Plivo (make sure to update the Auth Tokens, phone numbers, and ngrok URL):
     ```bash
     python plivo_make_call.py
     ```

---

**Note:** If you have a public URL for your application, ngrok is not required.

This setup allows seamless phonetic call testing using both Vonage and Plivo platforms.
