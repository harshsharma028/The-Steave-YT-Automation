import os
import re
import datetime
import logging
import sys

# Emoji in log messages crashes Windows' default cp1252 stdout whenever output
# isn't a real console (piped, redirected, scheduled runs). Force UTF-8 once,
# here, so every entry point into the pipeline is covered.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


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
    Create project folder: base/format/day_month_ProjectName/
    Example: projects/long form video/13_9_History_Weirdest_Laws/
    Returns the full path to the project directory.
    """
    format_dir = "short form video" if video_format == "short form" else "long form video"
    now = datetime.datetime.now()
    date_prefix = f"{now.day}_{now.month}"
    folder_name = f"{date_prefix}_{slugify(script_title)}"
    path = os.path.join(base_dir, format_dir, folder_name)

    # Avoid collisions if the same title is created twice on the same day
    final_path = path
    suffix = 2
    while os.path.exists(final_path):
        final_path = f"{path}_{suffix}"
        suffix += 1

    os.makedirs(final_path, exist_ok=True)
    return final_path

