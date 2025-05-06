"""TofuPilot integration with OpenHTF.

Core functionality:
1. upload(): Upload OpenHTF test results to TofuPilot
2. TofuPilot(): Stream real-time test execution data for monitoring
3. Enhanced prompts: Display interactive TofuPilot prompts in terminal
   - Bold question text with [User Input] prefix
   - Clickable TofuPilot URLs in the terminal
   - Instructions for terminal and web UI input options
   - Graceful Ctrl+C handling with result upload
"""

from .upload import upload
from .tofupilot import TofuPilot
from .custom_prompt import (
    patch_openhtf_prompts,
    prompt_with_tofupilot_url,
    enhanced_prompt_for_test_start,
)

__all__ = [
    'TofuPilot',
    'upload',
    'patch_openhtf_prompts',
    'prompt_with_tofupilot_url',
    'enhanced_prompt_for_test_start',
]
