import logging
import sys
from datetime import datetime

from tofupilot import TofuPilotClient


class TofuPilotLogHandler(logging.Handler):
    """Handler that captures logs in a format compatible with TofuPilot API."""

    def __init__(self):
        super().__init__()
        self.logs = []

    def emit(self, record):
        # Format log with ISO-8601 timestamp (UTC, ms) for TofuPilot API
        log_entry = {
            "level": record.levelname,
            "timestamp": datetime.utcfromtimestamp(record.created).isoformat(
                timespec="milliseconds"
            )
            + "Z",
            "message": record.getMessage(),
            "source_file": record.filename,
            "line_number": record.lineno,
        }
        self.logs.append(log_entry)


# Initialize the TofuPilot client to report test results
client = TofuPilotClient()

# Set up local logger with custom name and prevent propagation to parent
# loggers
local_logger = logging.getLogger("test_logger")
local_logger.setLevel(logging.DEBUG)
local_logger.propagate = False

# Add handlers: one for TofuPilot API capture and one for console output
capture_handler = TofuPilotLogHandler()
local_logger.addHandler(capture_handler)
local_logger.addHandler(logging.StreamHandler(sys.stdout))


# Log examples at different severity levels
local_logger.debug("Debug message: Detailed information for troubleshooting")
local_logger.info("Info message: Normal operation information")
local_logger.warning("Warning: Something unexpected but not critical")
local_logger.error("Error: A significant problem that needs attention")
local_logger.critical("Critical: System unstable, immediate action required")

# Create a run and send captured logs to TofuPilot
try:
    client.create_run(
        procedure_id="FVT1",
        unit_under_test={"serial_number": "00007035", "part_number": "LOGS01"},
        run_passed=True,
        logs=capture_handler.logs,
    )
finally:
    local_logger.removeHandler(capture_handler)
