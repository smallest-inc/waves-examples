import os
import argparse
import pandas as pd
from pathlib import Path
from tqdm import tqdm
from wvmos import get_wvmos
import torch
from .config import load_config
from .utils import setup_logger
from pydub import AudioSegment

logger = setup_logger(__name__)

def initialize_mos_model():
    """Initialize a single MOS model with automatic CUDA detection."""
    logger.info("Initializing MOS model...")
    cuda_available = torch.cuda.is_available()
    if cuda_available:
        logger.info("CUDA is available. Using GPU for MOS calculation.")
    else:
        logger.info("CUDA is not available. Using CPU for MOS calculation.")
    return get_wvmos(cuda=cuda_available)

def convert_mp3_to_temp_wav(mp3_path):
    """Convert MP3 to temporary WAV file for MOS calculation."""
    temp_dir = Path("temp_wav")
    temp_dir.mkdir(exist_ok=True)
    temp_wav = temp_dir / (mp3_path.stem + '_temp.wav')
    try:
        audio = AudioSegment.from_mp3(mp3_path)
        audio = audio.set_frame_rate(16000)  # Set to 16kHz as required by wvmos
        audio.export(temp_wav, format='wav')
        return temp_wav
    except Exception as e:
        logger.error(f"Error converting MP3 to WAV: {str(e)}")
        return None

def evaluate_directory(directory, mos_model, extension):
    """Evaluate all audio files in a directory."""
    results = []
    dir_path = Path(directory)
    audio_files = sorted(dir_path.glob(f"*.{extension}"))
    
    if extension == 'mp3':
        # Convert all MP3s to WAV first
        temp_wavs = []
        for audio_path in tqdm(audio_files, desc=f"Converting {directory} MP3s to WAV"):
            temp_wav = convert_mp3_to_temp_wav(audio_path)
            if temp_wav:
                temp_wavs.append((audio_path.name, temp_wav))
        
        # Calculate MOS for the temp directory
        if temp_wavs:
            temp_dir = Path("temp_wav")
            try:
                # Calculate MOS scores for individual files
                for orig_name, temp_wav in temp_wavs:
                    try:
                        score = float(mos_model.calculate_one(str(temp_wav)))
                        results.append({
                            'file': orig_name,
                            'provider': directory.split('/')[-1],
                            'mos_score': score
                        })
                    except Exception as e:
                        logger.error(f"Error calculating MOS for {orig_name}: {str(e)}")
                        results.append({
                            'file': orig_name,
                            'provider': directory.split('/')[-1],
                            'mos_score': None
                        })
            finally:
                # Clean up temp files
                for _, temp_wav in temp_wavs:
                    try:
                        temp_wav.unlink()
                    except:
                        pass
                temp_dir.rmdir()
    else:
        # For WAV files, calculate directly
        for audio_path in tqdm(audio_files, desc=f"Evaluating {directory}"):
            try:
                score = float(mos_model.calculate_one(str(audio_path)))
                results.append({
                    'file': audio_path.name,
                    'provider': directory.split('/')[-1],
                    'mos_score': score
                })
            except Exception as e:
                logger.error(f"Error calculating MOS for {audio_path.name}: {str(e)}")
                results.append({
                    'file': audio_path.name,
                    'provider': directory.split('/')[-1],
                    'mos_score': None
                })
    
    return results

def merge_with_test_data(results_df, test_csv_path):
    """Merge MOS results with original test data."""
    try:
        test_df = pd.read_csv(test_csv_path)
        
        # Extract index from filename (assuming format sample_XXXX.wav/mp3)
        results_df['index'] = results_df['file'].str.extract(r'sample_(\d+)').astype(int)
        test_df = test_df.reset_index()
        
        # Add test text to results if it exists in the test CSV
        if 'text' in test_df.columns:
            results_df = results_df.merge(
                test_df[['index', 'text']],
                on='index',
                how='left'
            )
        
        # Reorder columns
        base_cols = ['file', 'provider', 'mos_score']
        if 'text' in results_df.columns:
            base_cols.insert(2, 'text')
        results_df = results_df[base_cols + [c for c in results_df.columns if c not in base_cols and c != 'index']]
        
        return results_df
    except Exception as e:
        logger.error(f"Error merging with test data: {str(e)}")
        return results_df

def main():
    project_root = Path(__file__).parent.parent
    
    parser = argparse.ArgumentParser(description="Calculate MOS scores for generated audio samples")
    parser.add_argument("--test_csv", required=True, help="Path to CSV file with text and voice IDs")
    parser.add_argument("--config", default=str(project_root / "config" / "config.yaml"), help="Path to config file")
    args = parser.parse_args()

    # Load configuration
    config = load_config(args.config)
    
    # Initialize single MOS model
    mos_model = initialize_mos_model()
    
    # Create results directory
    Path("results").mkdir(exist_ok=True)
    
    # Evaluate directories with appropriate extensions
    all_results = []
    
    # Evaluate Smallest.ai WAV files
    if os.path.exists('generated/smallest'):
        results = evaluate_directory('generated/smallest', mos_model, 'wav')
        all_results.extend(results)
    
    # Evaluate ElevenLabs MP3 files
    if os.path.exists('generated/elevenlabs'):
        results = evaluate_directory('generated/elevenlabs', mos_model, 'mp3')
        all_results.extend(results)
    
    if not all_results:
        logger.error("No audio files found in generated directories!")
        return
    
    # Create results DataFrame
    results_df = pd.DataFrame(all_results)
    
    # Merge with test data to include original text
    results_df = merge_with_test_data(results_df, args.test_csv)
    
    # Calculate summary statistics
    summary = results_df.groupby('provider')['mos_score'].agg([
        'count', 'mean', 'std', 'min', 'max'
    ]).round(3)
    
    # Save results
    results_df.to_csv('results/detailed_mos_scores.csv', index=False)
    summary.to_csv('results/mos_summary.csv')
    
    # Print summary
    print("\nMOS Score Summary:")
    print(summary)
    
    # Print top/bottom samples (only include text if available)
    print("\nTop 5 Best Samples:")
    columns_to_show = ['provider', 'file', 'mos_score']
    if 'text' in results_df.columns:
        columns_to_show.insert(2, 'text')
    print(results_df.nlargest(5, 'mos_score')[columns_to_show])
    
    print("\nBottom 5 Samples:")
    print(results_df.nsmallest(5, 'mos_score')[columns_to_show])
    
    logger.info("Evaluation complete. Results saved to results/detailed_mos_scores.csv and results/mos_summary.csv")

if __name__ == "__main__":
    main()