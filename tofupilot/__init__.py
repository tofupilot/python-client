"""
This module initializes the TofuPilot package.

It imports the TofuPilotClient class which provides
the main interface for interacting with the TofuPilot API.
"""

from .client import TofuPilotClient
from .plugin import pass_fail_step, numeric_limit_step
