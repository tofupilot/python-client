"""
Deprecated TofuPilot API methods.

This module contains legacy methods that are deprecated and will be removed in v3.0.0.
Use the new API classes (runs, units, uploads, streaming, imports) instead.

See docs/api_migration.md for migration guide.
"""

from .legacy_client import LegacyMethods

__all__ = ["LegacyMethods"]
