# Smallest.ai Streaming API Example with Phonetic Call

This guide demonstrates how to use the **Smallest.ai Streaming API** with phonetic call functionality. It sets up a local FastAPI server that streams audio data and uses `ngrok` to expose the server for public testing. Both **Vonage** and **Plivo** are supported.

## Prerequisites

Ensure you have the following installed:

- **Python 3.7+**
- **ngrok** ([Download here](https://ngrok.com/download)) - used to expose localhost to the internet.

## General Steps

1. **Config:**
  - Create `.env` file with keys you want to run experiment of:
    ```bash
    SMALLEST_API_KEY=...
    PLIVO_AUTH_ID=...
    PLIVO_AUTH_TOKEN=...
    VONAGE_APPLICATION_ID=...
    ```
  - Add vonage to secrets to `secrets/private.key`

2. **Set up ngrok:**
   - Install `ngrok`, then run the command to expose your FastAPI server:
     ```bash
     ngrok http 8000  # For Vonage
     ngrok http 5000  # For Plivo
     ```

3. **Get the ngrok public URL:**
   - In the ngrok terminal, a public URL will be displayed, e.g., `https://abcd-1234-5678.ngrok.io`.


4. **Install the required dependencies:**
   - Run the following command to install the necessary Python packages:
     ```bash
     pip install -r requirements.txt
     ```

5. **Run the FastAPI application:**
   - For Vonage: 
     ```bash
     python vonage_example/vonage_app.py
     ```
   - For Plivo: **(Update the ngrok URL and path in the script first!)**
     ```bash
     python plivo_example/plivo_app.py
     ```

6. **Run the phonetic call client: (Update the phone numbers, ngrok URL and path in the script first!)**
   - For Vonage:
     ```bash
     python vonage_example/vonage_make_call.py
     ```
   - For Plivo:
     ```bash
     python plivo_example/plivo_make_call.py
     ```

---

**Note:** If you have a public URL for your application, ngrok is not required.

This setup allows seamless phonetic call testing using both Vonage and Plivo platforms.