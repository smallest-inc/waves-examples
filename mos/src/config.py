import yaml
from pathlib import Path

DEFAULT_CONFIG = {
    "smallest_key": None,
    "eleven_key": None,
    "max_retries": 3,
    "timeout": 30,
}

def load_config(config_path):
    """Load configuration from YAML file or use defaults."""
    config_path = Path(config_path)
    
    if not config_path.exists():
        print(f"Warning: Config file not found at {config_path}")
        print(f"Current working directory: {Path.cwd()}")
        print("Using default configuration.")
        return DEFAULT_CONFIG
        
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            if config is None:
                config = {}
            return {**DEFAULT_CONFIG, **config}  # Merge with defaults
    except Exception as e:
        print(f"Warning: Error reading config file: {str(e)}")
        print("Using default configuration.")
        return DEFAULT_CONFIG

def validate_config(config):
    """Validate configuration parameters."""
    required_keys = ['max_retries', 'timeout']
    
    missing_keys = [key for key in required_keys if key not in config]
    if missing_keys:
        raise ValueError(f"Missing required config keys: {missing_keys}")
    
    return True