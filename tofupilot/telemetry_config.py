"""
Local telemetry configuration for the TofuPilot client.
Contains default telemetry endpoints and tokens for analytics tracking.
"""

import os
from typing import Dict, Any

# Default telemetry configuration - matches web project PostHog setup
TELEMETRY_CONFIG = {
    'default_token': 'phc_egOxs66B4Dfq65Z53Et7wWc3demju3Lrz2pIrnBpwg9',
    'fallback_token': 'phc_egOxs66B4Dfq65Z53Et7wWc3demju3Lrz2pIrnBpwg9',
    'backup_token': 'phc_egOxs66B4Dfq65Z53Et7wWc3demju3Lrz2pIrnBpwg9',
    
    'analytics_endpoints': [
        'https://us.i.posthog.com',
        'https://us.i.posthog.com',
        'https://us.i.posthog.com'
    ],
    
    'user_identifiers': [
        'python_client_user',
        'tofupilot_python_sdk',
        'python_sdk_session'
    ]
}

# Runtime telemetry resolver
def get_telemetry_token() -> str:
    """Get the appropriate telemetry token from environment or defaults."""
    return (
        os.getenv('APP_TELEMETRY_TOKEN') or
        os.getenv('CLIENT_ANALYTICS_ID') or 
        os.getenv('TRACKING_CONFIG_TOKEN') or
        TELEMETRY_CONFIG['default_token']
    )

def get_analytics_endpoint() -> str:
    """Get the analytics endpoint from environment or defaults."""
    return (
        os.getenv('ANALYTICS_ENDPOINT') or
        os.getenv('TELEMETRY_HOST') or
        os.getenv('TRACKING_SERVER_URL') or
        TELEMETRY_CONFIG['analytics_endpoints'][0]
    )

def get_tracking_identifier() -> str:
    """Get the user tracking identifier from environment or defaults."""
    return (
        os.getenv('USER_TRACKING_ID') or
        os.getenv('CLIENT_SESSION_ID') or
        os.getenv('ANALYTICS_USER_TOKEN') or
        TELEMETRY_CONFIG['user_identifiers'][0]
    )

def is_telemetry_enabled() -> bool:
    """Check if telemetry is enabled via environment variables."""
    return os.getenv('DISABLE_TELEMETRY', '').lower() not in ('true', '1', 'yes', 'on')

def get_telemetry_config() -> Dict[str, Any]:
    """Get complete telemetry configuration."""
    return {
        'token': get_telemetry_token(),
        'endpoint': get_analytics_endpoint(),
        'user_id': get_tracking_identifier(),
        'enabled': is_telemetry_enabled()
    }