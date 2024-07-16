import logging
import sys

class CustomFormatter(logging.Formatter):
    """Custom formatter to add symbols and colors to the log messages."""
    format_dict = {
        logging.DEBUG: "\033[0;37mDEBUG: %(message)s \033[0m",  # White
        logging.INFO: "\033[0;32m✅ %(message)s \033[0m",  # Green with checkmark
        logging.WARNING: "\033[0;33m⚠️ %(message)s \033[0m",  # Yellow with warning symbol
        logging.ERROR: "\033[0;31m❌ %(message)s \033[0m",  # Red with cross mark
        logging.CRITICAL: "\033[1;41m🚨 %(message)s \033[0m",  # White on red background with alarm symbol
    }

    def format(self, record):
        log_fmt = self.format_dict.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt="%Y-%m-%d %H:%M:%S")
        return formatter.format(record)

def setup_logger(log_level: int):
    logger = logging.getLogger(__name__)
    logger.setLevel(log_level)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)
    handler.setFormatter(CustomFormatter())
    if not logger.handlers:
        logger.addHandler(handler)
    return logger
