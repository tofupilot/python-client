"""TofuPilot SDK with enhanced error tracking and logging capabilities."""

import os
from typing import Dict, Optional, Union
from .sdk import TofuPilot
from .sdkconfiguration import SDKConfiguration

from ..banner import print_banner_and_check_version

class TofuPilotWithErrorTracking(TofuPilot):
    """
    Enhanced TofuPilot client with automatic error tracking and improved logging.
    
    This wrapper extends the base TofuPilot SDK with:
    - Automatic error tracking and categorization
    - Enhanced logging for debugging
    - Better error context and suggestions
    - Transparent API - all original methods work exactly the same
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        server_url: Optional[str] = None,
        timeout_ms: Optional[int] = None,
        retry_config=None,
        debug: bool = False,
        **kwargs
    ):
        """
        Initialize TofuPilot client with error tracking.
        
        Args:
            api_key: API key for authentication
            server_url: Override default server URL
            timeout_ms: Request timeout in milliseconds
            retry_config: Retry configuration
            debug: Enable debug logging
            **kwargs: Additional arguments passed to base SDK
        """

        if api_key is None:
            api_key = os.environ.get("TOFUPILOT_API_KEY", None)

        # Initialize base SDK
        super().__init__(
            api_key=api_key,
            server_url=server_url,
            timeout_ms=timeout_ms,
            retry_config=retry_config,
            **kwargs
        )

        print_banner_and_check_version()
        
        # TODO: Add posthog to V2
