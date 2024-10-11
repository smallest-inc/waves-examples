# Livekit Example

This project provides scripts and tools to perform audio generation and assist with specific tasks. Follow the steps below to set up and run the project.

## Common Steps

### 1. Create a Virtual Environment

To ensure your Python environment is isolated, create a virtual environment:

```bash
python3 -m venv venv
```

Activate the virtual environment:

- On Linux/Mac:
  ```bash
  source venv/bin/activate
  ```

- On Windows:
  ```bash
  venv\Scripts\activate
  ```

### 2. Install Requirements

Once the virtual environment is activated, install the required dependencies:

```bash
pip install -r requirements.txt
```

### 3. Create a `.env` File

Create a `.env` file in the project root directory. This file should contain the following keys with appropriate values:

```bash
LIVEKIT_API_KEY=...
LIVEKIT_API_SECRET=...
LIVEKIT_URL=...
OPENAI_API_KEY=...
DEEPGRAM_API_KEY=...
SMALLEST_API_KEY=...
```

### 4. Install the plugin

To set up the livekit plugin for [smallest.ai](https://smallest.ai)

```bash
./install_plugin.sh
```

---

## Usage

### 1. Running `generate_audio.py`

To generate audio as a wav file, run the following command:

```bash
python3 generate_audio.py
```

You can change the parameters in the script and try out different voices, languages and texts.

### 2. Running `minimal_assistant.py`

To run the minimal assistant script, use this command:

```bash
python3 minimal_assistant.py start
```

---

## Notes

- Ensure that you have added the correct API keys and other credentials in the `.env` file before running the scripts.
- For any issues or questions, feel free to open an issue in the repository or contact the project maintainers.
```