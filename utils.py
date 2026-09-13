import os
import re
import datetime
import logging
import sys

def setup_logger(name):
    """
    Setup dual logging: console (clean) + file (detailed).
    Prevents duplicate logs by checking existing handlers.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        # Console: clean format
        console_fmt = logging.Formatter('[%(name)s] %(levelname)s: %(message)s')
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(console_fmt)
        logger.addHandler(console_handler)

        # File: detailed format with timestamp
        file_fmt = logging.Formatter('\n[%(asctime)s] === %(name)s ===\n%(levelname)s: %(message)s')
        file_handler = logging.FileHandler("pipeline.log", encoding='utf-8')
        file_handler.setFormatter(file_fmt)
        logger.addHandler(file_handler)

    return logger


def slugify(text):
    """
    Convert text → URL-safe slug (for folder names).
    Removes special chars, replaces spaces with underscores.
    """
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)  # Remove special chars
    text = re.sub(r'[\s_-]+', '_', text).strip('_')  # Consolidate separators
    return text


def create_project_folder(script_title, base_dir="projects", video_format="long form"):
    """
    Create timestamped project folder: base/format/date/title_timestamp/
    Returns the full path to the project directory.
    """
    format_dir = "short form video" if video_format == "short form" else "long form video"
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    folder_name = f"{slugify(script_title)}_{timestamp}"
    path = os.path.join(base_dir, format_dir, today, folder_name)
    os.makedirs(path, exist_ok=True)
    return path

