"""
Local telemetry configuration for the TofuPilot client.
"""

import os

def is_telemetry_enabled() -> bool:
    """Check if telemetry is enabled via environment variables."""
    return os.getenv('DISABLE_TELEMETRY', '').lower() not in ('true', '1', 'yes', 'on')
