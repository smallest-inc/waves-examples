import os
import argparse
import pandas as pd
from pathlib import Path
from tqdm import tqdm
from smallest import Smallest
from elevenlabs import ElevenLabs
from .config import load_config
from .utils import setup_logger

logger = setup_logger(__name__)

def setup_clients(config):
    """Initialize API clients with keys from config or environment variables."""
    smallest_key = config.get('smallest_key') or os.environ.get("SMALLEST_API_KEY")
    eleven_key = config.get('eleven_key') or os.environ.get("ELEVEN_API_KEY")
    
    if not smallest_key or not eleven_key:
        raise ValueError("API keys not found in config or environment variables")
    
    return Smallest(api_key=smallest_key), ElevenLabs(api_key=eleven_key)

def generate_audio(text, voice_id, client, provider, save_path):
    """Generate audio using specified provider and save to path."""
    try:
        if provider == "smallest":
            client.synthesize(text, voice=voice_id, save_as=save_path)
        else:  # elevenlabs
            audio = client.generate(text=text, voice=voice_id)
            with open(save_path, 'wb') as f:
                for chunk in audio:
                    f.write(chunk)
        return True
    except Exception as e:
        logger.error(f"Error generating audio for {provider} with voice {voice_id}: {str(e)}")
        return False

def main():
    # Get the project root directory (two levels up from this script)
    project_root = Path(__file__).parent.parent
    
    parser = argparse.ArgumentParser(description="Generate audio samples from Smallest.ai and ElevenLabs")
    parser.add_argument("--test_csv", required=True, help="Path to CSV file with text and voice IDs")
    parser.add_argument("--config", default=str(project_root / "config" / "config.yaml"), help="Path to config file")
    args = parser.parse_args()

    # Load configuration
    config = load_config(args.config)
    
    # Setup API clients
    client_smallest, client_eleven = setup_clients(config)
    
    # Create output directories
    Path("generated/smallest").mkdir(parents=True, exist_ok=True)
    Path("generated/elevenlabs").mkdir(parents=True, exist_ok=True)
    Path("results").mkdir(parents=True, exist_ok=True)
    
    # Read test data
    df = pd.read_csv(args.test_csv)
    required_columns = ['text', 'smallest_voice_id', '11labs_voice_id']
    if not all(col in df.columns for col in required_columns):
        raise ValueError(f"CSV must contain columns: {required_columns}")
    
    # Generate audio files
    results = []
    for idx, row in tqdm(df.iterrows(), total=len(df), desc="Generating audio"):
        sample_id = f"sample_{idx:04d}"
        
        # Generate Smallest.ai audio
        smallest_path = f"generated/smallest/{sample_id}.wav"
        smallest_success = generate_audio(
            row['text'], 
            row['smallest_voice_id'], 
            client_smallest, 
            "smallest", 
            smallest_path
        )
        
        # Generate ElevenLabs audio (as MP3)
        eleven_path = f"generated/elevenlabs/{sample_id}.mp3"
        eleven_success = generate_audio(
            row['text'], 
            row['11labs_voice_id'], 
            client_eleven, 
            "elevenlabs", 
            eleven_path
        )
        
        results.append({
            'sample_id': sample_id,
            'text': row['text'],
            'smallest_success': smallest_success,
            'elevenlabs_success': eleven_success
        })
    
    # Save generation results
    results_df = pd.DataFrame(results)
    results_df.to_csv('results/generation_results.csv', index=False)
    logger.info(f"Generated {len(results_df)} samples. Check generation_results.csv for details.")

if __name__ == "__main__":
    main()