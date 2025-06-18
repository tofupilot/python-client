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
    
    # Legacy API Methods (DEPRECATED - use new dotted notation)
    # These methods are maintained for backward compatibility
    
    def _deprecation_warning(self, old_method: str, new_method: str):
        """Show deprecation warning for legacy methods."""
        import warnings
        warnings.warn(
            f"'{old_method}' is deprecated and will be removed in v3.0.0. "
            f"Use '{new_method}' instead. See docs/api_migration.md for migration guide.",
            DeprecationWarning,
            stacklevel=3
        )
    
    # Runs API Legacy Methods
    
    def run_create(
        self, 
        serial_number: str,
        part_number: str,
        procedure_id: str = "default",
        outcome=None,
        phases=None,
        steps=None,
        procedure_version=None,
        started_at=None,
        duration_ms=None,
        sub_units=None,
        logs=None,
        **kwargs
    ):
        """
        Create a run (DEPRECATED).
        
        Use client.runs.create(body) instead.
        """
        self._deprecation_warning("client.run_create(...)", "client.runs.create(body)")
        
        from .models.run_create_body import RunCreateBody
        
        # Build the request body
        body_dict = {
            "unit_under_test": self._build_unit_under_test(serial_number, part_number),
            "procedure_id": procedure_id,
        }
        
        # Add optional fields
        if outcome is not None:
            body_dict["run_passed"] = self._convert_outcome_to_run_passed(outcome)
        if phases is not None:
            body_dict["phases"] = self._process_phases(phases)
        if steps is not None:
            body_dict["steps"] = self._process_steps(steps)
        if procedure_version is not None:
            body_dict["procedure_version"] = procedure_version
        if started_at is not None:
            body_dict["started_at"] = started_at
        if duration_ms is not None:
            body_dict["duration"] = self._convert_duration_ms_to_iso(duration_ms)
        if sub_units is not None:
            body_dict["sub_units"] = sub_units
        if logs is not None:
            body_dict["logs"] = logs
        
        # Add any additional kwargs
        body_dict.update(kwargs)
        
        body = RunCreateBody.from_dict(body_dict)
        return self.runs.create(body=body)
    
    def create_run(self, *args, **kwargs):
        """Alias for run_create (DEPRECATED)."""
        self._deprecation_warning("client.create_run(...)", "client.runs.create(body)")
        return self.run_create(*args, **kwargs)
    
    def run_delete_single(self, run_id: str):
        """
        Delete a single run (DEPRECATED).
        
        Use client.runs.delete(run_id) instead.
        """
        self._deprecation_warning("client.run_delete_single(run_id)", "client.runs.delete(run_id)")
        return self.runs.delete(run_id)
    
    def delete_run(self, run_id: str):
        """Alias for run_delete_single (DEPRECATED)."""
        self._deprecation_warning("client.delete_run(run_id)", "client.runs.delete(run_id)")
        return self.run_delete_single(run_id)
    
    def run_get_runs_by_serial_number(self, serial_number: str):
        """
        Get runs by serial number (DEPRECATED).
        
        Use client.runs.get_by_serial(serial_number) instead.
        """
        self._deprecation_warning("client.run_get_runs_by_serial_number(serial_number)", "client.runs.get_by_serial(serial_number)")
        return self.runs.get_by_serial(serial_number)
    
    def get_runs(self, serial_number: str):
        """Alias for run_get_runs_by_serial_number (DEPRECATED)."""
        self._deprecation_warning("client.get_runs(serial_number)", "client.runs.get_by_serial(serial_number)")
        return self.run_get_runs_by_serial_number(serial_number)
    
    # Units API Legacy Methods
    
    def unit_delete(self, serial_number: str):
        """
        Delete a unit (DEPRECATED).
        
        Use client.units.delete(serial_number) instead.
        """
        self._deprecation_warning("client.unit_delete(serial_number)", "client.units.delete(serial_number)")
        return self.units.delete(serial_number)
    
    def delete_unit(self, serial_number: str):
        """Alias for unit_delete (DEPRECATED)."""
        self._deprecation_warning("client.delete_unit(serial_number)", "client.units.delete(serial_number)")
        return self.unit_delete(serial_number)
    
    def unit_update_unit_parent(self, serial_number: str, sub_units):
        """
        Update unit parent relationships (DEPRECATED).
        
        Use client.units.update_parent(serial_number, body) instead.
        """
        self._deprecation_warning("client.unit_update_unit_parent(...)", "client.units.update_parent(serial_number, body)")
        
        from .models.unit_update_unit_parent_body import UnitUpdateUnitParentBody
        
        # Process sub_units to handle dict objects
        processed_sub_units = self._process_sub_units(sub_units)
        body = UnitUpdateUnitParentBody(sub_units=processed_sub_units)
        return self.units.update_parent(serial_number, body)
    
    def update_unit_parent(self, serial_number: str, sub_units):
        """Alias for unit_update_unit_parent (DEPRECATED)."""
        self._deprecation_warning("client.update_unit_parent(...)", "client.units.update_parent(serial_number, body)")
        return self.unit_update_unit_parent(serial_number, sub_units)
    
    # Uploads API Legacy Methods
    
    def upload_initialize(self, body):
        """
        Initialize upload (DEPRECATED).
        
        Use client.uploads.initialize(body) instead.
        """
        self._deprecation_warning("client.upload_initialize(body)", "client.uploads.initialize(body)")
        return self.uploads.initialize(body)
    
    def upload_sync_upload(self, body):
        """
        Sync upload (DEPRECATED).
        
        Use client.uploads.sync(body) instead.
        """
        self._deprecation_warning("client.upload_sync_upload(body)", "client.uploads.sync(body)")
        return self.uploads.sync(body)
    
    # Streaming API Legacy Methods
    
    def streaming_get_streaming_token(self):
        """
        Get streaming token (DEPRECATED).
        
        Use client.streaming.get_token() instead.
        """
        self._deprecation_warning("client.streaming_get_streaming_token()", "client.streaming.get_token()")
        return self.streaming.get_token()
    
    def get_streaming_token(self):
        """Alias for streaming_get_streaming_token (DEPRECATED)."""
        self._deprecation_warning("client.get_streaming_token()", "client.streaming.get_token()")
        return self.streaming_get_streaming_token()
    
    # Imports API Legacy Methods
    
    def run_create_from_file(self, file: bytes, importer: str):
        """
        Create run from file (DEPRECATED).
        
        Use client.imports.create_from_file(body) instead.
        """
        self._deprecation_warning("client.run_create_from_file(...)", "client.imports.create_from_file(body)")
        
        from .models.run_create_from_file_body import RunCreateFromFileBody
        
        body = RunCreateFromFileBody(file=file, importer=importer)
        return self.imports.create_from_file(body)
    
    def create_run_from_file(self, file: bytes, importer: str):
        """Alias for run_create_from_file (DEPRECATED)."""
        self._deprecation_warning("client.create_run_from_file(...)", "client.imports.create_from_file(body)")
        return self.run_create_from_file(file, importer)
    
    # Helper methods for legacy API compatibility
    
    def _build_unit_under_test(self, serial_number: str, part_number: str):
        """Build unit_under_test dict for legacy API."""
        return {
            "serial_number": serial_number,
            "part_number": part_number
        }
    
    def _convert_outcome_to_run_passed(self, outcome):
        """Convert outcome string to run_passed boolean."""
        if isinstance(outcome, bool):
            return outcome
        if isinstance(outcome, str):
            return outcome.upper() == "PASS"
        return bool(outcome)
    
    def _convert_duration_ms_to_iso(self, duration_ms):
        """Convert duration in milliseconds to ISO 8601 duration."""
        seconds = duration_ms / 1000
        return f"PT{seconds}S"
    
    def _process_measurements(self, measurements):
        """Process measurements to ensure proper format."""
        if not measurements:
            return measurements
            
        processed = []
        for measurement in measurements:
            if isinstance(measurement, dict):
                # Make a copy to avoid modifying the original
                measurement_copy = measurement.copy()
                
                # Add default outcome if missing
                if "outcome" not in measurement_copy:
                    # Determine outcome based on limits if present
                    measured_value = measurement_copy.get("measured_value")
                    lower_limit = measurement_copy.get("lower_limit")
                    upper_limit = measurement_copy.get("upper_limit")
                    
                    outcome = "PASS"  # Default to PASS
                    if measured_value is not None and isinstance(measured_value, (int, float)):
                        if lower_limit is not None and measured_value < lower_limit:
                            outcome = "FAIL"
                        elif upper_limit is not None and measured_value > upper_limit:
                            outcome = "FAIL"
                    
                    measurement_copy["outcome"] = outcome
                
                # Keep as dict for now, let the parent handle the conversion
                processed.append(measurement_copy)
            else:
                processed.append(measurement)
        return processed
    
    def _process_phases(self, phases):
        """Process phases to ensure proper format and add timing."""
        if not phases:
            return phases
            
        import time
        current_time_ms = int(time.time() * 1000)
        
        processed = []
        for i, phase in enumerate(phases):
            if isinstance(phase, dict):
                # Make a copy to avoid modifying the original
                phase_copy = phase.copy()
                
                # Add required timing fields if missing
                if "start_time_millis" not in phase_copy:
                    phase_copy["start_time_millis"] = current_time_ms + (i * 1000)
                if "end_time_millis" not in phase_copy:
                    phase_copy["end_time_millis"] = current_time_ms + ((i + 1) * 1000)
                
                # Process measurements if present
                if "measurements" in phase_copy:
                    phase_copy["measurements"] = self._process_measurements(phase_copy["measurements"])
                
                # Process attachments if present
                if "attachments" in phase_copy:
                    phase_copy["attachments"] = self._process_attachments(phase_copy["attachments"])
                
                # Keep as dict for now, let RunCreateBody.from_dict handle the conversion
                processed.append(phase_copy)
            else:
                processed.append(phase)
        return processed
    
    def _process_steps(self, steps):
        """Process steps to ensure proper format."""
        if not steps:
            return steps
            
        from datetime import datetime
        
        processed = []
        for step in steps:
            if isinstance(step, dict):
                # Make a copy to avoid modifying the original
                step_copy = step.copy()
                
                # Convert datetime objects or milliseconds to ISO format
                if "started_at" in step_copy:
                    started_at = step_copy["started_at"]
                    if isinstance(started_at, datetime):
                        # Convert datetime to ISO string
                        step_copy["started_at"] = started_at.isoformat()
                    elif isinstance(started_at, (int, float)):
                        # Convert milliseconds timestamp to ISO string
                        dt = datetime.fromtimestamp(started_at / 1000)
                        step_copy["started_at"] = dt.isoformat()
                
                # Keep as dict for now, let RunCreateBody.from_dict handle the conversion
                processed.append(step_copy)
            else:
                processed.append(step)
        return processed
    
    def _process_attachments(self, attachments):
        """Process attachments to ensure proper format."""
        if not attachments:
            return attachments
            
        import base64
        
        processed = []
        for attachment in attachments:
            if isinstance(attachment, dict):
                # Make a copy to avoid modifying the original
                attachment_copy = attachment.copy()
                
                # Convert bytes content to base64 string if present
                if "content" in attachment_copy and isinstance(attachment_copy["content"], bytes):
                    attachment_copy["content"] = base64.b64encode(attachment_copy["content"]).decode('utf-8')
                
                processed.append(attachment_copy)
            else:
                processed.append(attachment)
        return processed
    
    def _process_sub_units(self, sub_units):
        """Process sub_units to ensure proper format."""
        if not sub_units:
            return sub_units
            
        processed = []
        for sub_unit in sub_units:
            if isinstance(sub_unit, dict):
                # Convert dict to proper sub_unit object
                from .models.unit_update_unit_parent_body_sub_units_item import (
                    UnitUpdateUnitParentBodySubUnitsItem
                )
                processed.append(UnitUpdateUnitParentBodySubUnitsItem.from_dict(sub_unit))
            else:
                processed.append(sub_unit)
        return processed
