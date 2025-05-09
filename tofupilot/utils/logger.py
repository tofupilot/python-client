import logging
import sys
import os
import time
import threading
import queue
from datetime import datetime

# Define a custom log level for success messages
SUCCESS_LEVEL_NUM = 25
logging.addLevelName(SUCCESS_LEVEL_NUM, "SUCCESS")


def success(self, message, *args, **kws):
    """Log success at custom level."""
    if self.isEnabledFor(SUCCESS_LEVEL_NUM):
        self._log(SUCCESS_LEVEL_NUM, message, args, **kws)


logging.Logger.success = success


def add_pause_methods_to_logger(logger):
    """Add pause/resume functionality to a logger"""
    original_handlers = list(logger.handlers)
    
    def pause():
        """Temporarily disable all handlers"""
        for handler in logger.handlers:
            logger.removeHandler(handler)
    
    def resume():
        """Re-enable handlers"""
        for handler in original_handlers:
            if handler not in logger.handlers:
                logger.addHandler(handler)
    
    # Add methods to logger
    logger.pause = pause
    logger.resume = resume
    
    return logger


class LoggerStateManager:
    """Context manager for temporarily ensuring logger is active"""
    
    def __init__(self, logger):
        self.logger = logger
        self.was_resumed = False
        
    def __enter__(self):
        # Ensure logger is active for this block
        if hasattr(self.logger, 'resume'):
            self.logger.resume()
            self.was_resumed = True
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        # If we resumed the logger, restore to paused state
        if self.was_resumed and hasattr(self.logger, 'pause'):
            self.logger.pause()


class TofupilotFormatter(logging.Formatter):
    """Minimal formatter with colors and no timestamp."""

    # ANSI color codes
    RESET = "\033[0m"
    BLUE = "\033[0;34m"
    GREEN = "\033[0;32m"
    YELLOW = "\033[0;33m"
    RED = "\033[0;31m"
    RED_BG = "\033[1;41m"
    GRAY = "\033[0;37m"
    BOLD = "\033[1m"
    
    # Log level name mapping
    LEVEL_NAMES = {
        logging.DEBUG: "DBG",
        logging.INFO: "INF", 
        logging.WARNING: "WRN",
        logging.ERROR: "ERR",
        logging.CRITICAL: "CRT",
        SUCCESS_LEVEL_NUM: "OK!",
    }
    
    # Color mapping for levels
    LEVEL_COLORS = {
        logging.DEBUG: GRAY,
        logging.INFO: BLUE,
        logging.WARNING: YELLOW,
        logging.ERROR: RED,
        logging.CRITICAL: RED_BG,
        SUCCESS_LEVEL_NUM: GREEN,
    }
    
    def __init__(self):
        """Initialize formatter."""
        super().__init__()
        
    def format(self, record):
        """Format log with minimal prefix and colors."""
        # Get log level color and short name
        level_color = self.LEVEL_COLORS.get(record.levelno, self.RESET)
        level_name = self.LEVEL_NAMES.get(record.levelno, "???")
        
        # Create minimal prefix with no timestamp
        prefix = f"{level_color}{self.BOLD}TP{self.RESET}{level_color}:{level_name} "
        
        # Add log message with color
        message = record.getMessage()
        formatted_message = f"{prefix}{message}{self.RESET}"
        
        # Add exception info if present
        if record.exc_info:
            exc_text = self.formatException(record.exc_info)
            formatted_message += f"\n{exc_text}"
            
        return formatted_message


# Simple formatter for backward compatibility
class CustomFormatter(logging.Formatter):
    """Simple formatter with no timestamp."""

    reset_code = "\033[0m"

    format_dict = {
        logging.DEBUG: "\033[0;37mDEBUG: %(message)s" + reset_code,
        logging.INFO: "\033[0;34mINFO: %(message)s" + reset_code,
        logging.WARNING: "\033[0;33mWARN: %(message)s" + reset_code,
        logging.ERROR: "\033[0;31mERROR: %(message)s" + reset_code,
        logging.CRITICAL: "\033[1;41mCRIT: %(message)s" + reset_code,
        SUCCESS_LEVEL_NUM: "\033[0;32mSUCCESS: %(message)s" + reset_code,
    }

    def format(self, record):
        """Format record with minimal prefix."""
        log_fmt = self.format_dict.get(record.levelno, self._fmt)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


class LogLevelFilter(logging.Filter):
    """Sets log level from environment variable."""
    
    def __init__(self, env_var='TOFUPILOT_LOG_LEVEL'):
        """Init with env var name."""
        super().__init__()
        self.env_var = env_var
        self.level = self._get_level_from_env()
        
    def _get_level_from_env(self):
        """Get level from env var."""
        level_str = os.environ.get(self.env_var, 'INFO').upper()
        level_map = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO, 
            'SUCCESS': SUCCESS_LEVEL_NUM,
            'WARNING': logging.WARNING,
            'WARN': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
        return level_map.get(level_str, logging.INFO)
        
    def filter(self, record):
        """Apply dynamic level filtering."""
        # Reload level from env for each record to allow runtime changes
        self.level = self._get_level_from_env()
        return record.levelno >= self.level


def setup_logger(log_level=None, advanced_format=True):
    """Configure logger with minimal formatting and color support.
    
    Args:
        log_level: Override env var TOFUPILOT_LOG_LEVEL
        advanced_format: Use TofupilotFormatter (default) or CustomFormatter
    
    Returns:
        Configured logger instance
    """
    # Maintain backward compatibility with __name__
    logger_name = "tofupilot"
    logger = logging.getLogger(logger_name)
    
    # Clear existing handlers
    if logger.handlers:
        logger.handlers.clear()
    
    # Set level from arg or environment
    level_filter = LogLevelFilter()
    log_level = log_level or level_filter.level
    logger.setLevel(log_level)
    
    # Create handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)
    
    # Choose formatter based on preference
    if advanced_format:
        handler.setFormatter(TofupilotFormatter())
    else:
        handler.setFormatter(CustomFormatter())
        
    handler.addFilter(level_filter)
    
    # Add handler to logger
    logger.addHandler(handler)
    
    # Add pause/resume functionality
    logger = add_pause_methods_to_logger(logger)
    
    return logger