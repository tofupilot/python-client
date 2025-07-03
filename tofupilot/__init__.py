"""
This module initializes the TofuPilot package.

It imports the TofuPilotClient class which provides
the main interface for interacting with the TofuPilot API.
"""

from .client import TofuPilotClient
from .models import MeasurementOutcome, PhaseOutcome
from .plugin import conf, numeric_step, string_step

# Explicit exports for linting
__all__ = ["TofuPilotClient", "MeasurementOutcome", "PhaseOutcome", "conf", "numeric_step", "string_step"]

# Version is set dynamically by CI
try:
    from importlib.metadata import version

    __version__ = version("tofupilot")
except Exception:
    # Fallback for development
    __version__ = "0.0.0.dev"
