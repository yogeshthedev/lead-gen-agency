import logging
import os
from datetime import datetime

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def get_logger(name: str) -> logging.Logger:
    """
    Returns a logger that writes to both terminal and a log file.
    Usage: logger = get_logger(__name__)
    """
    os.makedirs("logs", exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if logger.handlers:
        return logger  # already set up

    fmt = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Terminal handler
    console = logging.StreamHandler()
    console.setFormatter(fmt)
    logger.addHandler(console)

    # File handler — one log file per day
    today = datetime.now().strftime("%Y-%m-%d")
    file_handler = logging.FileHandler(f"logs/{today}.log")
    file_handler.setFormatter(fmt)
    logger.addHandler(file_handler)

    return logger
