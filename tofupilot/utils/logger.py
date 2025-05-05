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

    def __init__(self, handler: logging.Handler):
        #super().__init__()
        self._wrapped = handler
        self._paused = False
        self._buffer = queue.Queue()

    def emit(self, record):
        if self._paused:
            self._buffer.put(record)
        else:
            self._wrapped.emit(record)

    def pause(self):
        self._paused = True

    def resume(self):
        self._paused = False
        while not self._buffer.empty():
            self._wrapped(self._buffer.get())

    def close(self):
        self._wrapped.close()
        # super().close()

    @property
    def level(self):
        return self._wrapped.level
    
    @property
    def name(self):
        return self._wrapped.name

    @name.setter
    def name(self, value):
        self._wrapped.name = value

    def createLock(self):
        self._wrapped.createLock()

    def acquire(self):
        self._wrapped.acquire()

    def release(self):
        self._wrapped.release()

    def setLevel(self, level):
        self._wrapped.setLevel(level)

    def format(self, record):
        return self._wrapped.format(record)

    def handle(self, record):
        return self._wrapped.handle(record)

    def setFormatter(self, fmt):
        self._wrapped.setFormatter(fmt)

    def flush(self):
        self._wrapped.flush()

    def close(self):
        self._wrapped.close()

    def handleError(self, record):
        self._wrapped.handleError(record)

    def __repr__(self):
        return repr(self._wrapped)
    
    def addFilter(self, filter):
        self._wrapped.addFilter(filter)

    def removeFilter(self, filter):
        self._wrapped.removeFilter(filter)

    def filter(self, record):
        return self._wrapped.filter(record)



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
    handler = PausableHandler(logging.StreamHandler(sys.stdout))
    handler.setLevel(log_level)
    handler.setFormatter(CustomFormatter())
    if not logger.handlers:
        logger.addHandler(handler)

    logger.pause = handler.pause
    logger.resume = handler.resume

    return logger
