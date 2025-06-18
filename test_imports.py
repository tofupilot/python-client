#!/usr/bin/env python3
"""Test script to demonstrate different import methods after package installation."""

print("Testing different import methods for TofuPilot client:\n")

# Method 1: Shortest import (after our changes)
try:
    from tofupilot import TofuPilotClient
    print("✓ from tofupilot import TofuPilotClient")
    print(f"  Class location: {TofuPilotClient.__module__}")
except ImportError as e:
    print(f"✗ from tofupilot import TofuPilotClient")
    print(f"  Error: {e}")

print()

# Method 2: Current import method
try:
    from tofupilot_client import TofuPilotClient
    print("✓ from tofupilot_client import TofuPilotClient")
    print(f"  Class location: {TofuPilotClient.__module__}")
except ImportError as e:
    print(f"✗ from tofupilot_client import TofuPilotClient")
    print(f"  Error: {e}")

print()

# Method 3: Full path import (current working method)
try:
    from tofupilot_client.openapi_client import TofuPilotClient
    print("✓ from tofupilot_client.openapi_client import TofuPilotClient")
    print(f"  Class location: {TofuPilotClient.__module__}")
except ImportError as e:
    print(f"✗ from tofupilot_client.openapi_client import TofuPilotClient")
    print(f"  Error: {e}")

print("\nNote: Run 'pip install -e .' in the python-client directory to test these imports.")