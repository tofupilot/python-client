"""
This module handles all TofuPilot methods related to integration with OpenHTF.

It provides two main classes:
1. tofupilot.upload(): A way to interface with OpenHTF test scripts to automatically upload test results to the TofuPilot server.
2. tofupilot.TofuPilot(): A way to stream real-time execution data of OpenHTF tests to TofuPilot for live monitoring.
"""

from .upload import upload
from .tofupilot import TofuPilot
