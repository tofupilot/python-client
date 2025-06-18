"""
Legacy TofuPilot API methods.

This module contains all deprecated methods that will be removed in v3.0.0.
Use the new API classes (runs, units, uploads, streaming, imports) instead.
"""

import warnings
from datetime import datetime
from typing import Any, Optional


class LegacyMethods:
    """Mixin class providing legacy API methods with deprecation warnings."""

    def _deprecation_warning(self, old_method: str, new_method: str):
        """Show deprecation warning for legacy methods."""
        warnings.warn(
            f"'{old_method}' is deprecated and will be removed in v3.0.0. "
            f"Use '{new_method}' instead. "
            f"See docs/api_migration.md for migration guide.",
            DeprecationWarning,
            stacklevel=3,
        )

    def _convert_duration_ms_to_iso(self, duration_ms: Optional[int]) -> Optional[str]:
        """Convert duration in milliseconds to ISO 8601 duration string."""
        if duration_ms is None:
            return None
        seconds = duration_ms / 1000
        return f"PT{seconds}S"

    def _convert_outcome_to_run_passed(self, outcome: Optional[str]) -> Optional[bool]:
        """Convert outcome string to run_passed boolean."""
        if outcome is None:
            return None
        return outcome.upper() == "PASS"

    def _build_unit_under_test(self, serial_number: str, part_number: str) -> dict[str, str]:
        """Build unit_under_test dict from convenience parameters."""
        return {"serial_number": serial_number, "part_number": part_number}

    # Legacy Runs API Methods

    def run_create(
        self,
        serial_number: str,
        part_number: str,
        procedure_name: Optional[str] = None,
        procedure_version: Optional[str] = None,
        outcome: Optional[str] = None,
        started_at: Optional[str] = None,
        duration: Optional[int] = None,
        phases: Optional[list[dict[str, Any]]] = None,
        steps: Optional[list[dict[str, Any]]] = None,
        sub_units: Optional[list[dict[str, str]]] = None,
        **kwargs,
    ):
        """
        Create a new run (DEPRECATED).

        Use client.runs.create(body) instead.
        """
        self._deprecation_warning("client.run_create(...)", "client.runs.create(body)")

        from ..openapi_client.models.run import Run

        # Build unit_under_test from convenience parameters
        unit_under_test = self._build_unit_under_test(serial_number, part_number)

        # Process complex fields
        processed_phases = self._process_phases(phases) if phases else None
        processed_steps = self._process_steps(steps) if steps else None
        processed_sub_units = self._process_sub_units(sub_units) if sub_units else None

        # Convert convenience parameters to the expected format
        run_passed = self._convert_outcome_to_run_passed(outcome)
        duration_iso = self._convert_duration_ms_to_iso(duration)

        # Build the body dict and use from_dict to handle flexible parameters
        body_dict = {
            "unit_under_test": unit_under_test,
        }

        # Add optional fields conditionally
        if procedure_name is not None:
            body_dict["procedure_name"] = procedure_name
        else:
            # Set a default procedure_id if neither procedure_name nor procedure_id is provided
            body_dict["procedure_id"] = "default"

        if procedure_version is not None:
            body_dict["procedure_version"] = procedure_version
        if run_passed is not None:
            body_dict["run_passed"] = run_passed
        if started_at is not None:
            body_dict["started_at"] = started_at
        if duration_iso is not None:
            body_dict["duration"] = duration_iso
        if processed_phases is not None:
            body_dict["phases"] = processed_phases
        if processed_steps is not None:
            body_dict["steps"] = processed_steps
        if processed_sub_units is not None:
            body_dict["sub_units"] = processed_sub_units

        # Add any additional kwargs
        body_dict.update(kwargs)

        body = Run.from_dict(body_dict)

        return self.runs.create(body)

    def create_run(self, *args, **kwargs):
        """Alias for run_create (DEPRECATED)."""
        return self.run_create(*args, **kwargs)

    def run_delete_single(self, run_id: str):
        """Delete a run by ID (DEPRECATED)."""
        self._deprecation_warning("client.run_delete_single(run_id)", "client.runs.delete(run_id)")
        return self.runs.delete(run_id)

    def delete_run(self, run_id: str):
        """Alias for run_delete_single (DEPRECATED)."""
        return self.run_delete_single(run_id)

    def run_get_runs_by_serial_number(self, serial_number: str):
        """
        Get runs by serial number (DEPRECATED).

        Use client.runs.get_by_serial(serial_number) instead.
        """
        self._deprecation_warning(
            "client.run_get_runs_by_serial_number(serial_number)", "client.runs.get_by_serial(serial_number)"
        )
        return self.runs.get_by_serial(serial_number)

    def get_runs(self, serial_number: str):
        """Alias for run_get_runs_by_serial_number (DEPRECATED)."""
        return self.run_get_runs_by_serial_number(serial_number)

    # Legacy Units API Methods

    def unit_delete(self, serial_number: str):
        """
        Delete a unit by serial number (DEPRECATED).

        Use client.units.delete(serial_number) instead.
        """
        self._deprecation_warning("client.unit_delete(serial_number)", "client.units.delete(serial_number)")
        return self.units.delete(serial_number)

    def delete_unit(self, serial_number: str):
        """Alias for unit_delete (DEPRECATED)."""
        return self.unit_delete(serial_number)

    def unit_update_unit_parent(self, serial_number: str, sub_units: list[dict[str, str]]):
        """
        Update unit parent relationships (DEPRECATED).

        Use client.units.update_parent(serial_number, body) instead.
        """
        self._deprecation_warning(
            "client.unit_update_unit_parent(...)", "client.units.update_parent(serial_number, body)"
        )

        from ..openapi_client.models.unit_update_unit_parent_body import UnitUpdateUnitParentBody

        # Process sub_units to handle dict objects
        processed_sub_units = self._process_sub_units(sub_units)
        body = UnitUpdateUnitParentBody(sub_units=processed_sub_units)
        return self.units.update_parent(serial_number, body)

    def update_unit_parent(self, serial_number: str, sub_units: list[dict[str, str]]):
        """Alias for unit_update_unit_parent (DEPRECATED)."""
        return self.unit_update_unit_parent(serial_number, sub_units)

    # Legacy Uploads API Methods

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

    # Legacy Streaming API Methods

    def streaming_get_streaming_token(self):
        """
        Get streaming token (DEPRECATED).

        Use client.streaming.get_token() instead.
        """
        self._deprecation_warning("client.streaming_get_streaming_token()", "client.streaming.get_token()")
        return self.streaming.get_token()

    def get_streaming_token(self):
        """Alias for streaming_get_streaming_token (DEPRECATED)."""
        return self.streaming_get_streaming_token()

    # Legacy Imports API Methods

    def run_create_from_file(self, body):
        """
        Create run from file (DEPRECATED).

        Use client.imports.create_from_file(body) instead.
        """
        self._deprecation_warning("client.run_create_from_file(...)", "client.imports.create_from_file(body)")
        return self.imports.create_from_file(body)

    def create_run_from_file(self, body):
        """Alias for run_create_from_file (DEPRECATED)."""
        return self.run_create_from_file(body)

    # Helper methods for processing data

    def _process_measurements(self, measurements):
        """Process measurements to ensure proper format."""
        if not measurements:
            return measurements

        processed = []
        for measurement in measurements:
            if isinstance(measurement, dict):
                # Make a copy and add default outcome if missing
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

                processed.append(measurement_copy)
            else:
                processed.append(measurement)
        return processed

    def _process_phases(self, phases):
        """Process phases to ensure proper format and add default timing."""
        if not phases:
            return phases

        import time

        current_time_ms = int(time.time() * 1000)

        processed = []
        for i, phase in enumerate(phases):
            if isinstance(phase, dict):
                # Make a copy to avoid modifying the original
                phase_copy = phase.copy()

                # Add default timing if not present
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

        processed = []
        for step in steps:
            if isinstance(step, dict):
                # Make a copy to avoid modifying the original
                step_copy = step.copy()

                # Convert started_at from milliseconds to ISO format if it's an integer
                if "started_at" in step_copy:
                    started_at = step_copy["started_at"]
                    if isinstance(started_at, int):
                        # Convert from milliseconds timestamp to ISO format
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
                    attachment_copy["content"] = base64.b64encode(attachment_copy["content"]).decode("utf-8")

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
                # Keep as dict for now, let the model handle the conversion
                processed.append(sub_unit)
            else:
                processed.append(sub_unit)
        return processed
