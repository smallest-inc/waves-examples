# Pipecat Quickstart

Test Smallest AI Integrations with Pipecat locally. 

> 🎯 Quick start: Local bot in 5 minutes

### Prerequisites

#### Environment

- Python 3.10 or later
- [uv](https://docs.astral.sh/uv/getting-started/installation/) package manager installed

#### AI Service API keys

You'll need API keys from three services:

- [Smallest](https://console.smallest.ai/apikeys) for Text-to-Speech and Speech-to-Text
- [OpenAI](https://auth.openai.com/create-account) for LLM inference

### Setup

Navigate to the quickstart directory and set up your environment.

1. Install dependencies:

   ```bash
   uv sync
   ```

2. Configure your API keys:

   Create a `.env` file:

   ```bash
   cp env.example .env
   ```

   Then, add your API keys:

   ```ini
   SMALLEST_API_KEY=your_smallest_api_key
   OPENAI_API_KEY=your_openai_api_key
   ```

### Run your bot locally

```bash
uv run bot.py
```

**Open http://localhost:7860 in your browser** and click `Connect` to start talking to your bot.

> 💡 First run note: The initial startup may take ~20 seconds as Pipecat downloads required models and imports.

🎉 **Success!** Your bot is running locally. Now let's deploy it to production so others can use it.