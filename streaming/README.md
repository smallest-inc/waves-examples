# Streaming TTS with Lightning Large Model

This guide demonstrates how to stream text-to-speech (TTS) audio using the Lightning Large model via Smallest AI's Waves API.

## Overview

The Lightning Large model provides high-quality text-to-speech capabilities with streaming support, allowing you to start playing audio before the entire speech generation is complete.

## Prerequisites

- Python 3.6+
- Smallest AI API key
- Required packages: `requests` and `pydub`

## Installation

Install the required dependencies:

```bash
pip install requests pydub
```

## Usage

The `streaming_api.py` script demonstrates how to use the streaming API to convert text to speech and save the result as a WAV file.

### Basic Usage

1. Replace the placeholder values in the script:
    - `<TEXT>` with the text you want to convert to speech
    - `<VOICE>` with your chosen voice ID
    - `<AUTH TOKEN>` with your Smallest AI API key

2. Run the script:

```bash
python streaming_api.py
```

The script will output a file named `output.wav` containing the generated speech.

### Configuration Options

The payload supports the following parameters:

| Parameter | Description | Default |
|-----------|-------------|---------|
| `text` | The text to convert to speech | Required |
| `voice_id` | The ID of the voice to use | Required |
| `sample_rate` | Audio sample rate in Hz | 24000 |
| `speed` | Speech speed multiplier | 1 |
| `language` | Language code | "en" |
| `consistency` | Voice consistency factor (0-1) | 0.5 |
| `similarity` | Voice similarity factor (0-1) | 0 |
| `enhancement` | Audio enhancement level (0-1) | 1 |

## How It Works

1. The script sends a POST request to the streaming endpoint
2. The API responds with a stream of audio chunks
3. Each chunk is decoded and written to a WAV file
4. The script measures performance metrics like TTFB

## Custom Implementation

To implement streaming in your own application:

```python
from streaming_api import stream

payload = {
     "text": "Hello, world!",
     "voice_id": "your_voice_id",
     "sample_rate": 24000,
}

headers = {
     "Authorization": "Bearer your_api_key",
     "Content-Type": "application/json"
}

stream(payload, headers)
```

## Troubleshooting

If you encounter issues:

- Verify your API key is valid
- Check that the voice ID is available for Lightning Large
- Ensure your text doesn't exceed maximum length
- Check your internet connection

For additional help, contact Smallest AI support.