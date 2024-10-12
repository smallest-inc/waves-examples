# Livekit Example

This Example provides scripts and tools to perform standalone audio generation and build livekit voice assistants using the smallest's livekit plugin. Follow the steps below to set up and run the experiments.   
Please also refer to [smallest.ai](https://smallest.ai) plugin integration PR in the [livekit/agents](https://github.com/livekit/agents/pull/890) repository.  

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

### 3. Sign in and create a new project on livekit and copy the following tokens:   
Sign in here: https://cloud.livekit.io/

```
LIVEKIT_API_KEY
LIVEKIT_API_SECRET
LIVEKIT_URL
```

### 4. Create a `.env` File

Create a `.env` file in the project root directory. This file should contain the following keys with appropriate values:

```bash
LIVEKIT_API_KEY=...
LIVEKIT_API_SECRET=...
LIVEKIT_URL=...
OPENAI_API_KEY=...
DEEPGRAM_API_KEY=...
SMALLEST_API_KEY=...
```

### 5. Install the plugin

To set up the livekit plugin for [smallest.ai](https://smallest.ai)

```bash
./install_plugin.sh
```

---

## Usage

### 1. Running `generate_audio.py`

To generate audio using the smallest.ai plugin as a wav file, run the following command:

```bash
python3 generate_audio.py
```

You can change the parameters in the script and try out different voices, languages and texts.

### 2. Running `minimal_assistant.py`

To buid a minimal livekit voice assistant using the smallest model, run the following command:

```bash
python3 minimal_assistant.py dev
```  
  
### 3. Connect to the agent here:   

https://agents-playground.livekit.io/



---

## Notes

- Ensure that you have added the correct API keys and other credentials in the `.env` file before running the scripts.
- For any issues or questions, feel free to open an issue in the repository or contact us.
