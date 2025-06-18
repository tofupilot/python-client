"""TofuPilot integration with OpenHTF.

It provides two main classes:
1. upload(): Upload OpenHTF test results to TofuPilot
2. TofuPilot(): Stream real-time test execution data for monitoring
"""

from .tofupilot import TofuPilot
from .upload import upload

__all__ = ["TofuPilot", "upload"]
