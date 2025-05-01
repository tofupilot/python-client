import logging
import sys
import queue

# Define a custom log level for success messages
SUCCESS_LEVEL_NUM = 25
logging.addLevelName(SUCCESS_LEVEL_NUM, "SUCCESS")


def success(self, message, *args, **kws):
    """Log a success message."""
    if self.isEnabledFor(SUCCESS_LEVEL_NUM):
        self._log(SUCCESS_LEVEL_NUM, message, args, **kws)


logging.Logger.success = success

class PausableHandler(logging.Handler):
    def __init__(self, wrapped_handler):
        super().__init__()
        self._wrapped_handler = wrapped_handler
        self._paused = False
        self._buffer = []

    def emit(self, record):
        if self._paused:
            self._buffer.append(record)
        else:
            self._wrapped_handler.emit(record)

    def pause(self):
        self._paused = True

    def resume(self):
        self._paused = False
        while self._buffer:
            record = self._buffer.pop(0)
            self._wrapped_handler.emit(record)

    def setFormatter(self, fmt):
        self._wrapped_handler.setFormatter(fmt)

    def flush(self):
        self._wrapped_handler.flush()

    def close(self):
        self._wrapped_handler.close()
        super().close()


def pausable(underlying: logging.Handler):
    oldEmit = underlying.emit

    underlying.paused = False


    underlying.paused_record_queue = queue.Queue()

    def pause():
        print("paused")
        underlying.paused = True

    underlying.pause = pause

    def unpause():
        print("unpaused")
        if (underlying.paused):
            while not underlying.paused_record_queue.empty():
                oldEmit(underlying.paused_record_queue.get())

    underlying.unpause = unpause

    def newEmit(record: logging.LogRecord):

        if (underlying.paused):
            underlying.paused_record_queue.put(record)
        else:
            return oldEmit(record)

    underlying.emit = newEmit

    return underlying

class CustomFormatter(logging.Formatter):
    """Custom formatter to add symbols and colors to the log messages."""

    reset_code = "\033[0m"

    format_dict = {
        logging.DEBUG: "\033[0;37m%(asctime)s - DEBUG: %(message)s"
        + reset_code,  # White
        logging.INFO: "\033[0;34m%(asctime)s - ℹ️ %(message)s"
        + reset_code,  # Blue with info symbol
        logging.WARNING: "\033[0;33m%(asctime)s - ⚠️ %(message)s"
        + reset_code,  # Yellow with warning symbol
        logging.ERROR: "\033[0;31m%(asctime)s - ❌ %(message)s"
        + reset_code,  # Red with cross mark
        logging.CRITICAL: "\033[1;41m%(asctime)s - 🚨 %(message)s"
        + reset_code,  # White on red background with alarm symbol
        SUCCESS_LEVEL_NUM: "\033[0;32m%(asctime)s - ✅ %(message)s"
        + reset_code,  # Green with checkmark
    }

    def format(self, record):
        """Format the specified record as text."""
        log_fmt = self.format_dict.get(record.levelno, self._fmt)
        formatter = logging.Formatter(log_fmt, datefmt="%Y-%m-%d %H:%M:%S")
        return formatter.format(record)


def setup_logger(log_level: int):
    """Set up the logger with a custom formatter and stream handler."""
    logger = logging.getLogger(__name__)
    logger.setLevel(log_level)
    handler = pausable(logging.StreamHandler(sys.stdout))
    handler.setLevel(log_level)
    handler.setFormatter(CustomFormatter())
    if not logger.handlers:
        logger.addHandler(handler)

    return logger
