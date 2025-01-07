import logging
from pathlib import Path

def setup_logger(name):
    """Set up logger with consistent formatting."""
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        # Create logs directory
        Path("logs").mkdir(exist_ok=True)
        
        # File handler
        fh = logging.FileHandler('logs/app.log')
        fh.setLevel(logging.INFO)
        
        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        logger.addHandler(fh)
        logger.addHandler(ch)
    
    return logger

def validate_audio_file(file_path):
    """Validate that an audio file exists and is readable."""
    path = Path(file_path)
    if not path.exists():
        return False, f"File {file_path} does not exist"
    if not path.suffix.lower() in ['.wav', '.mp3']:
        return False, f"File {file_path} is not an audio file"
    return True, None