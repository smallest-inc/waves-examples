# TTS MOS Evaluation

This repository provides tools to generate and evaluate text-to-speech (TTS) samples from Smallest.ai and ElevenLabs using MOS (Mean Opinion Score) metrics. It uses the WVMOS model for quality evaluation.

## Features

- Generate audio samples from both Smallest.ai and ElevenLabs APIs
- Evaluate audio quality using WVMOS (Wav-based MOS predictor)
- Support for both WAV and MP3 audio formats
- Detailed logging and result analysis
- Comprehensive result reporting

## Directory Structure
```
tts-mos-evaluation/
├── main.py                 # Entry point script
├── README.md              # Project documentation
├── requirements.txt       # Python dependencies
├── config/
│   └── config.yaml       # Configuration file
├── data/                 # Directory for input data
│   └── test.csv         # Sample test CSV file
├── generated/            # Generated audio files
│   ├── smallest/        # WAV files from Smallest.ai
│   └── elevenlabs/      # MP3 files from ElevenLabs
├── results/             # Output results
│   ├── detailed_mos_scores.csv
│   ├── mos_summary.csv
│   └── generation_results.csv
├── logs/                # Log files
│   └── app.log
└── src/                 # Source code
    ├── __init__.py
    ├── generate.py      # Audio generation script
    ├── evaluate.py      # MOS evaluation script
    ├── utils.py        # Utility functions
    └── config.py       # Configuration handling
```

## Setup

1. Clone the repository:
```bash
git clone https://github.com/smallest-inc/waves-examples.git
cd waves-examples/mos
```

2. Install dependencies:
```bash
# First install wvmos
pip install git+https://github.com/AndreevP/wvmos

# Then install other requirements
pip install -r requirements.txt
```

3. Set up your API keys:
   - Option 1: Add them to `config/config.yaml`:
     ```yaml
     smallest_key: "YOUR_SMALLEST_API_KEY"
     eleven_key: "YOUR_ELEVEN_LABS_API_KEY"
     ```
   - Option 2: Set environment variables:
     ```bash
     export SMALLEST_API_KEY="your_smallest_key"
     export ELEVEN_API_KEY="your_eleven_key"
     ```

## Usage

### Preparing Input Data

Create a CSV file with the following columns:
- `text`: The text to synthesize
- `smallest_voice_id`: Voice ID for Smallest.ai
- `11labs_voice_id`: Voice ID for ElevenLabs

Example `data/sample_data.csv`:
```csv
text,smallest_voice_id,11labs_voice_id
Hello world,emily,Adam
Welcome to TTS,john,Rachel
```

### Running the Pipeline

1. Run the complete pipeline (generation + evaluation):
```bash
python main.py --test_csv data/sample_data.csv
```

2. Skip audio generation and only evaluate existing audio:
```bash
python main.py --test_csv data/sample_data.csv --skip_generation
```

3. Skip evaluation and only generate audio:
```bash
python main.py --test_csv data/sample_data.csv --skip_evaluation
```

4. Use a custom config file:
```bash
python main.py --test_csv data/sample_data.csv --config path/to/config.yaml
```

### Output Files

1. Audio files:
   - `generated/smallest/*.wav`: WAV files from Smallest.ai
   - `generated/elevenlabs/*.mp3`: MP3 files from ElevenLabs

2. Results:
   - `results/detailed_mos_scores.csv`: Individual MOS scores for each file
   - `results/mos_summary.csv`: Statistical summary by provider
   - `results/generation_results.csv`: Generation success/failure log

3. Logs:
   - `logs/app.log`: Detailed application logs

## Configuration

The `config/config.yaml` file supports the following options:
```yaml
# API Keys (alternatively set via environment variables)
smallest_key: null  # Smallest.ai API key
eleven_key: null   # ElevenLabs API key

# Audio Generation Settings
max_retries: 3  # Maximum number of retries for failed generations
timeout: 30  # Timeout in seconds for API calls
```

## Results Format

### Detailed MOS Scores (detailed_mos_scores.csv)
```csv
file,provider,text,mos_score
sample_0001.wav,smallest,Hello world,4.32
sample_0001.mp3,elevenlabs,Hello world,4.45
```

### Summary Statistics (mos_summary.csv)
```csv
provider,count,mean,std,min,max
elevenlabs,5,4.133,0.313,3.825,4.487
smallest,5,4.587,0.376,4.133,4.937
```

## Troubleshooting

1. **API Key Issues**:
   - Ensure API keys are correctly set in config.yaml or environment variables
   - Check API key permissions and quotas

2. **Audio Generation Errors**:
   - Check the logs/app.log file for detailed error messages
   - Verify voice IDs exist in the respective platforms
   - Check API rate limits and quotas

3. **MOS Evaluation Issues**:
   - Ensure CUDA is available if using GPU
   - Check audio file format compatibility
   - Verify audio sample rates

## Citations

This project uses WVMOS for MOS prediction:
```
@article{andreev2022wvmos,
  title={WV-MOS: Predicting Speech Quality by Learning from Non-Intrusive Human Ratings},
  author={Andreev, Pavel and Patakin, Nikolay and Desheulin, Oleg and Kagan, Alexander and Bulanbaev, Arthur},
  journal={arXiv preprint arXiv:2203.13086},
  year={2022}
}
```
