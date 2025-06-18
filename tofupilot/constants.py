"""
Configuration constants for the TofuPilot client.

This module defines all configuration constants used throughout the TofuPilot client.
"""

# API Configuration
ENDPOINT = "https://www.tofupilot.app"

# File upload limits
FILE_MAX_SIZE = 100 * 1024 * 1024  # 100MB in bytes (updated from production client)
CLIENT_MAX_ATTACHMENTS = 50  # Updated from production client

# Network configuration
SECONDS_BEFORE_TIMEOUT = 300  # 5 minutes (updated from production client)

__all__ = [
    "ENDPOINT",
    "FILE_MAX_SIZE", 
    "CLIENT_MAX_ATTACHMENTS",
    "SECONDS_BEFORE_TIMEOUT",
]