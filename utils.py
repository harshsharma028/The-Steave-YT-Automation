import os
import re
import datetime
import logging
import sys

def setup_logger(name):
    """
    Sets up a standardized logger for the pipeline.
    Includes proper spacing (\n) to make reading logs easier.
    Logs are printed to the console and saved to 'pipeline.log'.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Only add handlers if they don't already exist to prevent duplicate logs
    if not logger.handlers:
        # Formatter with newlines for visual spacing
        formatter = logging.Formatter(
            '\n[%(asctime)s] === %(name)s ===\n%(levelname)s: %(message)s'
        )
        
        # Console Handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # File Handler
        file_handler = logging.FileHandler("pipeline.log", encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
    return logger

def slugify(text):
    """
    Converts text to a URL-friendly slug.
    Used for creating safe folder names.
    """
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '_', text).strip('_')
    return text

def create_project_folder(script_title, base_dir="projects"):
    """
    Creates a timestamped project folder to store all generated assets.
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    folder_name = f"{slugify(script_title)}_{timestamp}"
    path = os.path.join(base_dir, folder_name)
    os.makedirs(path, exist_ok=True)
    return path
