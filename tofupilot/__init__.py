"""
This module initializes the TofuPilot package.

It imports the TofuPilotClient class which provides
the main interface for interacting with the TofuPilot API.
"""

from .client import TofuPilotClient
from .upload import UploadToTofuPilot
from .plugin import numeric_step, string_step, conf
