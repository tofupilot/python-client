"""
This module handles all TofuPilot methods related to integration with OpenHTF.

It provides the following functionality:
1. tofupilot.upload(): A way to interface with OpenHTF test scripts to automatically upload test results to the TofuPilot server.
2. tofupilot.TofuPilot(): A way to stream real-time execution data of OpenHTF tests to TofuPilot for live monitoring.
3. Enhanced prompts: Automatically include TofuPilot URLs in OpenHTF prompts, making it easy for test operators to access the live view.
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
