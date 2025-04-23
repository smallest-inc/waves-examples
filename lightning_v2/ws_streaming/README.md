# Websocket Streaming TTS with Lightning-V2 Model

This guide demonstrates how to use text-to-speech (TTS) using Websocket audio using the Lightning V2 model via Smallest AI's Waves API.

## Overview

The Lightning V2 model provides high-quality text-to-speech capabilities with streaming support, allowing you to start playing audio before the entire speech generation is complete.

## Prerequisites

- Python 3.6+
- Smallest AI API key
- Required packages: `websocket-client`

## Installation

Install the required dependencies:

```bash
pip install websocket-client
```

## Usage

The `ws_streaming_api.py` script demonstrates how to use the streaming API to convert text to speech and save the result as a WAV file.

### Basic Usage

1. Replace the placeholder values in the script:
    - `<TEXT>` with the text you want to convert to speech
    - `<VOICE>` with your chosen voice ID
    - `<AUTH TOKEN>` with your Smallest AI API key

2. Run the script:

```bash
python ws_streaming_api.py
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

1. The script first creates three-way handshake with Web Socket
2. Then it sends the payload to WebSocket
3. Each chunk is decoded and written to a WAV file
4. The script measures performance metrics like TTFB
5. When connection is closed, it saves the audio as `output.wav`

## Troubleshooting

If you encounter issues:

- Verify your API key is valid
- Check that the voice ID is available for Lightning V2
- Ensure your text doesn't exceed maximum length
- Check your internet connection

For additional help, contact Smallest AI support.