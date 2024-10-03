# Smallest.ai Streaming API Example with Phonetic Call

This repository demonstrates how to use the **Smallest.ai Streaming API** with phonetic call functionality. The example sets up a local FastAPI server that streams audio data, and then uses the `ngrok` service to expose it to the public for testing.

## Prerequisites

Before starting, ensure you have the following tools installed:

- Python 3.7+
- [ngrok](https://ngrok.com/download) (to expose localhost to the internet)


Download and install ngrok if you haven't already. Once installed, run the following command to expose your FastAPI server:

#### 1. Set up ngrok

```
ngrok http 8000
```

#### 2. Install the required dependencies

```
pip install -r requirements.txt
```

#### 3. Run the FastAPI application

```
python app.py
```

#### 4. Use ngrok to get the public URL

In the ngrok terminal, you'll see a public URL that looks something like this:

```
https://abcd-1234-5678.ngrok.io
```

#### 5. Run the phonetic call client

```
python make_call.py
```

**Note:** It can be also directly used without ngork, if application is running with public url
