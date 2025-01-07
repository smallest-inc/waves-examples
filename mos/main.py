import argparse
from pathlib import Path
import sys
import time
from src.generate import main as generate_main
from src.evaluate import main as evaluate_main
from src.utils import setup_logger

logger = setup_logger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Generate and evaluate TTS samples")
    parser.add_argument("--test_csv", required=True, help="Path to CSV file with text and voice IDs")
    parser.add_argument("--config", default="config/config.yaml", help="Path to config file")
    parser.add_argument("--skip_generation", action="store_true", help="Skip audio generation and only run evaluation")
    parser.add_argument("--skip_evaluation", action="store_true", help="Skip evaluation and only generate audio")
    args = parser.parse_args()

    # Convert args to dict for passing to sub-functions
    args_dict = vars(args).copy()

    start_time = time.time()

    try:
        # Audio Generation
        if not args.skip_generation:
            logger.info("Starting audio generation...")
            generate_main()
            logger.info("Audio generation completed.")
        
        # MOS Evaluation
        if not args.skip_evaluation:
            logger.info("Starting MOS evaluation...")
            evaluate_main()
            logger.info("MOS evaluation completed.")
        
        end_time = time.time()
        total_time = end_time - start_time
        logger.info(f"Total processing time: {total_time:.2f} seconds")

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()