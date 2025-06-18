"""
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
