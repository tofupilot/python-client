"""TofuPilot integration with OpenHTF.

It provides the following functions and classes:
1. withTofuPilot(): Convenience function to run OpenHTF tests with TofuPilot integration
2. upload(): Upload OpenHTF test results to TofuPilot
3. TofuPilot(): Stream real-time test execution data for monitoring (context manager)
4. execute_with_graceful_exit(): Helper for better Ctrl+C handling
"""

from .upload import upload
from .tofupilot import TofuPilot, withTofuPilot, execute_with_graceful_exit

__all__ = ["upload", "TofuPilot", "withTofuPilot", "execute_with_graceful_exit"]
