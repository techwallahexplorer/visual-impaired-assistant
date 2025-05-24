import os
from pathlib import Path
import kaggle
import logging
import json
import time

class DataLoader:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.cache_dir = Path("cache")
        self.cache_dir.mkdir(exist_ok=True)
        self._setup_kaggle_auth()
        
    def _setup_kaggle_auth(self):
        """Setup Kaggle authentication with better error handling"""
        try:
            # Check if kaggle.json exists
            kaggle_path = Path.home() / '.kaggle' / 'kaggle.json'
            if not kaggle_path.exists():
                self.logger.error(f"Kaggle API credentials not found at {kaggle_path}")
                raise FileNotFoundError(
                    f"Please place your kaggle.json file at {kaggle_path}. "
                    "You can download it from https://www.kaggle.com/account"
                )
            
            # Check file permissions
            if os.name == 'posix':  # For Unix-like systems
                os.chmod(kaggle_path, 0o600)
            
            # Validate JSON format
            with open(kaggle_path) as f:
                creds = json.load(f)
                if 'username' not in creds or 'key' not in creds:
                    raise ValueError("Invalid kaggle.json format. File should contain 'username' and 'key'")
            
            # Set environment variable
            os.environ['KAGGLE_CONFIG_DIR'] = str(Path.home() / '.kaggle')
            
        except Exception as e:
            self.logger.error(f"Error setting up Kaggle authentication: {e}")
            raise
        
    def load_datasets(self):
        """Load both audio and training datasets with proper cache handling"""
        try:
            self.load_audio_dataset()
            self.load_training_dataset()
        except Exception as e:
            self.logger.error(f"Error loading datasets: {e}")
            raise
    
    def load_audio_dataset(self):
        """Load audio dataset with cache handling and retries"""
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                self.logger.info(f"Loading audio dataset (attempt {attempt + 1}/{max_retries})...")
                
                # Download dataset
                kaggle.api.authenticate()
                kaggle.api.dataset_download_files(
                    'mozilla/common_voice',
                    path=str(self.cache_dir / "audio"),
                    unzip=True,
                    quiet=False
                )
                
                self.audio_dataset = str(self.cache_dir / "audio")
                self.logger.info("Audio dataset loaded successfully")
                return
                
            except Exception as e:
                self.logger.warning(f"Attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    self.logger.error("All attempts to load audio dataset failed")
                    self.audio_dataset = None
                    raise
    
    def load_training_dataset(self):
        """Load training dataset with cache handling and retries"""
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                self.logger.info(f"Loading training dataset (attempt {attempt + 1}/{max_retries})...")
                
                # Download dataset
                kaggle.api.authenticate()
                kaggle.api.dataset_download_files(
                    'google/fleurs',
                    path=str(self.cache_dir / "training"),
                    unzip=True,
                    quiet=False
                )
                
                self.training_dataset = str(self.cache_dir / "training")
                self.logger.info("Training dataset loaded successfully")
                return
                
            except Exception as e:
                self.logger.warning(f"Attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    self.logger.error("All attempts to load training dataset failed")
                    self.training_dataset = None
                    raise
    
    def get_training_data(self):
        """Get processed training data"""
        if not hasattr(self, 'training_dataset') or self.training_dataset is None:
            return []
        return self.training_dataset
