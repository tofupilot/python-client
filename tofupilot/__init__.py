"""TofuPilot Python Client Library.

This package provides both v1 and v2 API clients:
- v1: Legacy client for backward compatibility
- v2: New Speakeasy-generated SDK with enhanced features and error tracking

For new projects, we recommend using the v2 client.

Telemetry and Error Tracking:
Both clients support telemetry and error tracking. Configure with environment variables:
- APP_TELEMETRY_TOKEN: Your telemetry project token
- ANALYTICS_ENDPOINT: Analytics host (defaults to standard endpoint)
- USER_TRACKING_ID: User identifier for tracking (defaults to 'telemetry_user_001')

Disable telemetry: DISABLE_TELEMETRY=true

Or configure programmatically using configure_error_tracking().
"""

__version__ = "2.0.0"

# Import v1 client for backward compatibility
from .v1.client import TofuPilotClient
from .v1.models import MeasurementOutcome, PhaseOutcome
from .v1 import responses, models, client, constants

import sys as _sys
_sys.modules['tofupilot.responses'] = responses
_sys.modules['tofupilot.models'] = models
_sys.modules['tofupilot.client'] = client
_sys.modules['tofupilot.constants'] = constants
_sys.modules['tofupilot.responses.responses'] = responses.responses
_sys.modules['tofupilot.models.models'] = models.models
_sys.modules['tofupilot.constants.attachments'] = constants.attachments
_sys.modules['tofupilot.constants.requests'] = constants.requests

# Import pytest plugin
from .pytest import TofuPilotPlugIn

from . import v2
