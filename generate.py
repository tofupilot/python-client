#!/usr/bin/env python3
"""
Generate TofuPilot Python client.

This script generates a Python client from the TofuPilot OpenAPI specification
and creates a custom wrapper with dotted notation for easier usage.
"""

import os
import subprocess
import sys
from pathlib import Path

# Configuration
OPENAPI_URL = os.getenv("OPENAPI_URL", "http://localhost:3000/api/v1/openapi.json")
OUTPUT_DIR = Path(__file__).parent / "tofupilot"
CONFIG_FILE = Path(__file__).parent / "openapi-generator-config.yaml"


def generate_client() -> None:
    """Generate TofuPilot Python client."""
    print(f"Generating TofuPilot Python client from: {OPENAPI_URL}")
    
    cmd = [
        "openapi-python-client",
        "generate",
        "--url", OPENAPI_URL,
        "--output-path", str(OUTPUT_DIR),
        "--config", str(CONFIG_FILE),
        "--overwrite",
    ]
    
    try:
        subprocess.run(cmd, check=True)
        create_dotted_client()
        update_init()
        
        # Remove auto-generated README if it exists
        readme_path = OUTPUT_DIR / "README.md"
        if readme_path.exists():
            readme_path.unlink()
            print("🗑️  Removed auto-generated README.md")
        
        print("✅ Client generated successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Generation failed: {e}")
        sys.exit(1)


def create_dotted_client() -> None:
    """Create the client wrapper."""
    client_content = '''"""
TofuPilot API client.
"""

from typing import Optional, Union
from .client import AuthenticatedClient, Client as BaseClient


class RunsAPI:
    """Runs API."""
    
    def __init__(self, client: Union[AuthenticatedClient, BaseClient]):
        self._client = client
    
    def create(self, body):
        from .api.runs.run_create import sync_detailed
        return sync_detailed(client=self._client, body=body)
    
    def get_by_serial(self, serial_number: str):
        from .api.runs.run_get_runs_by_serial_number import sync_detailed
        return sync_detailed(client=self._client, serial_number=serial_number)
    
    def delete(self, run_id: str):
        from .api.runs.run_delete_single import sync_detailed
        return sync_detailed(client=self._client, id=run_id)


class UnitsAPI:
    """Units API."""
    
    def __init__(self, client: Union[AuthenticatedClient, BaseClient]):
        self._client = client
    
    def delete(self, serial_number: str):
        from .api.units.unit_delete import sync_detailed
        return sync_detailed(client=self._client, serial_number=serial_number)
    
    def update_parent(self, serial_number: str, body):
        from .api.units.unit_update_unit_parent import sync_detailed
        return sync_detailed(client=self._client, serial_number=serial_number, body=body)


class UploadsAPI:
    """Uploads API."""
    
    def __init__(self, client: Union[AuthenticatedClient, BaseClient]):
        self._client = client
    
    def initialize(self, body):
        from .api.uploads.upload_initialize import sync_detailed
        return sync_detailed(client=self._client, body=body)
    
    def sync(self, body):
        from .api.uploads.upload_sync_upload import sync_detailed
        return sync_detailed(client=self._client, body=body)


class StreamingAPI:
    """Streaming API."""
    
    def __init__(self, client: Union[AuthenticatedClient, BaseClient]):
        self._client = client
    
    def get_token(self):
        from .api.streaming.streaming_get_streaming_token import sync_detailed
        return sync_detailed(client=self._client)


class ImportsAPI:
    """Imports API."""
    
    def __init__(self, client: Union[AuthenticatedClient, BaseClient]):
        self._client = client
    
    def create_from_file(self, body):
        from .api.imports.run_create_from_file import sync_detailed
        return sync_detailed(client=self._client, body=body)


class TofuPilotClient(AuthenticatedClient):
    """
    TofuPilot API client.
    
    Example:
        client = TofuPilotClient(api_key="tp_1234567890abcdef")
        response = client.runs.get_by_serial("DEMO-001")
    """
    
    def __init__(self, api_key: str, base_url: str = "http://localhost:3000", **kwargs):
        # Ensure base_url ends with /api/v1
        if not base_url.endswith('/api/v1'):
            base_url = base_url.rstrip('/') + '/api/v1'
        super().__init__(base_url=base_url, token=api_key, **kwargs)
        self.runs = RunsAPI(self)
        self.units = UnitsAPI(self)
        self.uploads = UploadsAPI(self)
        self.streaming = StreamingAPI(self)
        self.imports = ImportsAPI(self)
'''
    
    client_file = OUTPUT_DIR / "openapi_client" / "tofu_client.py"
    client_file.write_text(client_content)


def update_init() -> None:
    """Update __init__.py to export TofuPilotClient."""
    init_content = '''""" A client library for accessing TofuPilot API v1 """
from .tofu_client import TofuPilotClient

__all__ = ("TofuPilotClient",)
'''
    
    init_file = OUTPUT_DIR / "openapi_client" / "__init__.py"
    init_file.write_text(init_content)


if __name__ == "__main__":
    generate_client()