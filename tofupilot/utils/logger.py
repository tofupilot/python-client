import logging
import sys
import os
import time
import threading
from datetime import datetime

# Define a custom log level for success messages
SUCCESS_LEVEL_NUM = 25
logging.addLevelName(SUCCESS_LEVEL_NUM, "SUCCESS")


def success(self, message, *args, **kws):
    """Log success at custom level."""
    if self.isEnabledFor(SUCCESS_LEVEL_NUM):
        self._log(SUCCESS_LEVEL_NUM, message, args, **kws)


logging.Logger.success = success


class TofupilotFormatter(logging.Formatter):
    """Dev-friendly formatter with colors, timing, and thread info."""

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
        """Init with timing trackers."""
        super().__init__()
        self.start_time = time.time()
        self.lock = threading.Lock()
        # Thread local storage for timing information
        self.local = threading.local()
        self.local.last_time = self.start_time
        
    def format(self, record):
        """Format log with timing, colors and thread info."""
        # Calculate timing information - thread safe
        current_time = time.time()
        
        # Initialize thread-local storage for first access
        if not hasattr(self.local, 'last_time'):
            self.local.last_time = self.start_time
            
        # Calculate elapsed times
        elapsed_total = current_time - self.start_time
        elapsed_since_last = current_time - self.local.last_time
        self.local.last_time = current_time
        
        # Get log level color and short name
        level_color = self.LEVEL_COLORS.get(record.levelno, self.RESET)
        level_name = self.LEVEL_NAMES.get(record.levelno, "???")
        
        # Get thread name/id for concurrent operations
        thread_info = ""
        if threading.active_count() > 1:
            current_thread = threading.current_thread()
            if current_thread.name != "MainThread":
                thread_info = f"[{current_thread.name}] "
        
        # Format time as HH:MM:SS.mmm
        time_str = datetime.fromtimestamp(record.created).strftime("%H:%M:%S.%f")[:-3]
        
        # Construct log message with contextual information
        elapsed_str = f"+{elapsed_since_last:.3f}s"
        prefix = f"{level_color}{time_str} {self.BOLD}TP{self.RESET}{level_color}:{level_name} {elapsed_str} {thread_info}"
        
        # Add log message
        message = record.getMessage()
        formatted_message = f"{prefix}{message}{self.RESET}"
        
        # Add exception info if present
        if record.exc_info:
            exc_text = self.formatException(record.exc_info)
            formatted_message += f"\n{exc_text}"
            
        return formatted_message


# Legacy formatter for backward compatibility
class CustomFormatter(logging.Formatter):
    """Custom formatter with minimal styling."""

    reset_code = "\033[0m"

    format_dict = {
        logging.DEBUG: "\033[0;37m%(asctime)s - DEBUG: %(message)s" + reset_code,
        logging.INFO: "\033[0;34m%(asctime)s - INFO: %(message)s" + reset_code,
        logging.WARNING: "\033[0;33m%(asctime)s - WARN: %(message)s" + reset_code,
        logging.ERROR: "\033[0;31m%(asctime)s - ERROR: %(message)s" + reset_code,
        logging.CRITICAL: "\033[1;41m%(asctime)s - CRIT: %(message)s" + reset_code,
        SUCCESS_LEVEL_NUM: "\033[0;32m%(asctime)s - SUCCESS: %(message)s" + reset_code,
    }

    def format(self, record):
        """Format the specified record as text."""
        log_fmt = self.format_dict.get(record.levelno, self._fmt)
        formatter = logging.Formatter(log_fmt, datefmt="%Y-%m-%d %H:%M:%S")
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
    """Configure logger with timing, thread tracking and color support.
    
    Args:
        log_level: Override env var TOFUPILOT_LOG_LEVEL
        advanced_format: Use advanced formatting (default True)
    
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
    if log_level is not None:
        logger.setLevel(log_level)
    else:
        logger.setLevel(level_filter.level)
    
    # Create stdout handler
    handler = logging.StreamHandler(sys.stdout)
    
    # Choose formatter based on preference
    if advanced_format:
        handler.setFormatter(TofupilotFormatter())
    else:
        handler.setFormatter(CustomFormatter())
        
    handler.addFilter(level_filter)
    
    # Add handler to logger
    logger.addHandler(handler)
    
    return logger