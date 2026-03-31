"""
TofuPilot v1 API client module.

This module provides access to the v1 TofuPilot client for backwards compatibility
and explicit version management.
"""

from .client import TofuPilotClient

__all__ = ["TofuPilotClient"]