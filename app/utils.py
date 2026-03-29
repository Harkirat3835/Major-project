import nltk
import logging
from typing import NoReturn
import os
from pathlib import Path

logger = logging.getLogger(__name__)

def setup_logging():
    """Setup application logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('app.log', mode='a')
        ]
    )

def download_nltk_data():
    """Download required NLTK data"""
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        logger.info("Downloading NLTK punkt tokenizer...")
        nltk.download('punkt', quiet=True)

    try:
        nltk.data.find('tokenizers/punkt_tab')
    except (LookupError, OSError):
        logger.info("punkt_tab tokenizer not found, falling back to punkt tokenizer...")
        nltk.download('punkt', quiet=True)

    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        logger.info("Downloading NLTK stopwords...")
        nltk.download('stopwords', quiet=True)

    try:
        nltk.data.find('corpora/wordnet')
    except LookupError:
        logger.info("Downloading NLTK wordnet...")
        nltk.download('wordnet', quiet=True)

def ensure_directories():
    """Ensure required directories exist"""
    dirs = ['model', 'data', 'logs', 'app/__pycache__']
    for dir_name in dirs:
        os.makedirs(dir_name, exist_ok=True)
        logger.info(f"Ensured directory exists: {dir_name}")

def validate_environment():
    """Validate that required files and dependencies exist"""
    required_files = [
        'model/model.pkl',
        'model/vectorizer.pkl'
    ]

    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)

    if missing_files:
        logger.warning(f"Missing model files: {', '.join(missing_files)}. Will attempt to train on first use.")
    else:
        logger.info("Environment validation passed")

def get_project_root():
    """Get the project root directory"""
    return Path(__file__).parent.parent

def format_timestamp(timestamp):
    """Format timestamp for display"""
    from datetime import datetime
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

def calculate_accuracy_stats():
    """Calculate accuracy statistics from feedback data"""
    # This would be implemented to calculate user feedback accuracy
    # For now, return placeholder stats
    return {
        'overall_accuracy': 0.95,
        'total_predictions': 0,
        'correct_predictions': 0,
        'user_feedback_count': 0
    }