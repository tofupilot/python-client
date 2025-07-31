"""Test unit GET endpoint."""

import pytest
import time
from datetime import datetime, timezone
from tofupilot.v2 import TofuPilot
from tofupilot.v2.errors import ErrorNOTFOUND
from ...utils import assert_create_run_success, assert_station_access_limited, get_random_test_dates


class TestGetUnit:
    """Test retrieving individual units by serial number."""

    def test_get_existing_unit(self, client: TofuPilot, procedure_id: str, auth_type: str):
        """Test retrieving an existing unit by its serial number."""
        # Create a unit via run with unique serial number
        timestamp = str(int(time.time() * 1000000))
        serial_number = f"TEST-UNIT-GET-{timestamp}"
        started_at, ended_at = get_random_test_dates()
        run_response = client.runs.create(
            outcome="PASS",
            procedure_id=procedure_id,
            serial_number=serial_number,
            part_number=f"TEST-PART-{timestamp}",
            revision_number="REV-A",
            started_at=started_at,
            ended_at=ended_at
        )
        assert_create_run_success(run_response)
        
        # Get the unit by serial number
        unit = client.units.get(serial_number=serial_number)
        
        # Verify response
        assert unit.serial_number == serial_number
        assert unit.id is not None
        assert unit.created_at is not None
        
        # Verify part information
        assert unit.part is not None
        assert unit.part.number == f"TEST-PART-{timestamp}"
        assert unit.part.name is not None
        assert unit.part.revision.number == "REV-A"

    def test_get_unit_with_parent_children(self, client: TofuPilot, procedure_id: str, auth_type: str):
        """Test retrieving a unit with parent/child relationships."""
        # Create parent unit with unique serial
        timestamp = str(int(time.time() * 1000000))
        parent_serial = f"PARENT-UNIT-{timestamp}"
        started_at, ended_at = get_random_test_dates()
        parent_run = client.runs.create(
            outcome="PASS",
            procedure_id=procedure_id,
            serial_number=parent_serial,
            part_number=f"PARENT-PART-{timestamp}",
            started_at=started_at,
            ended_at=ended_at
        )
        assert_create_run_success(parent_run)
        
        # Create child units
        child_serials = [f"CHILD-{timestamp}-001", f"CHILD-{timestamp}-002"]
        for serial in child_serials:
            try:
                started_at, ended_at = get_random_test_dates()
                run = client.runs.create(
                    outcome="PASS",
                    procedure_id=procedure_id,
                    serial_number=serial,
                    part_number=f"CHILD-PART-{timestamp}",
                    started_at=started_at,
                    ended_at=ended_at
                )
                assert_create_run_success(run)
            except Exception as e:
                if auth_type == "station":
                    # Stations may not have permission to create multiple runs with the same part number
                    with assert_station_access_limited("create runs with duplicate part numbers"):
                        raise e
                    return
                else:
                    raise
        
        # Create main unit with parent and children
        main_serial = f"MAIN-UNIT-{timestamp}"
        try:
            started_at, ended_at = get_random_test_dates()
            main_run = client.runs.create(
                outcome="PASS",
                procedure_id=procedure_id,
                serial_number=main_serial,
                part_number=f"MAIN-PART-{timestamp}",
                sub_units=child_serials,
                started_at=started_at,
                ended_at=ended_at
            )
            assert_create_run_success(main_run)
        except Exception as e:
            if auth_type == "station":
                # Stations may not have permission to create runs with sub_units
                with assert_station_access_limited("create runs with sub_units"):
                    raise e
                return
            else:
                raise
        
        # Get the main unit
        unit = client.units.get(serial_number=main_serial)
        
        # Verify parent/child relationships
        assert unit.parent is None  # Main unit has no parent
        assert len(unit.children) == 2
        
        child_serial_numbers = [child.serial_number for child in unit.children]
        assert set(child_serial_numbers) == set(child_serials)

    def test_get_unit_with_runs(self, client: TofuPilot, procedure_id: str, auth_type: str):
        """Test retrieving a unit includes its run history."""
        timestamp = str(int(time.time() * 1000000))
        serial_number = f"TEST-UNIT-RUNS-{timestamp}"
        
        # Create multiple runs for the same unit
        outcomes = ["PASS", "FAIL", "PASS"]
        for i, outcome in enumerate(outcomes):
            # Use different durations for variety
            started_at, ended_at = get_random_test_dates(duration_minutes=5 + i)
            run = client.runs.create(
                outcome=outcome,  # type: ignore[arg-type]
                procedure_id=procedure_id,
                serial_number=serial_number,
                part_number=f"TEST-PART-{timestamp}",
                started_at=started_at,
                ended_at=ended_at
            )
            assert_create_run_success(run)
        
        # Get the unit
        unit = client.units.get(serial_number=serial_number)
        
        # Verify runs
        assert len(unit.runs) == 3
        
        # Verify run details
        run_outcomes = [run.outcome for run in unit.runs]
        assert set(run_outcomes) == {"PASS", "FAIL"}
        
        for run in unit.runs:
            assert run.id is not None
            assert run.created_at is not None
            assert run.started_at is not None
            assert run.duration is not None
            assert run.procedure is not None
            assert run.procedure.id == procedure_id

    def test_get_unit_with_batch(self, client: TofuPilot, procedure_id: str, auth_type: str):
        """Test retrieving a unit that belongs to a batch."""
        # Create batch with unique number
        timestamp = str(int(time.time() * 1000000))
        batch_number = f"TEST-BATCH-UNIT-{timestamp}"
        batch_response = client.batches.create(number=batch_number)
        assert batch_response.id is not None
        
        # Create unit in batch
        serial_number = f"UNIT-IN-BATCH-{timestamp}"
        started_at, ended_at = get_random_test_dates()
        run = client.runs.create(
            outcome="PASS",
            procedure_id=procedure_id,
            serial_number=serial_number,
            part_number=f"TEST-PART-{timestamp}",
            batch_number=batch_number,
            started_at=started_at,
            ended_at=ended_at
        )
        assert_create_run_success(run)
        
        # Get the unit
        unit = client.units.get(serial_number=serial_number)
        
        # Verify batch
        assert unit.batch is not None
        assert unit.batch.number == batch_number  # type: ignore[union-attr]
        assert unit.batch.id is not None  # type: ignore[union-attr]

    def test_get_nonexistent_unit(self, client: TofuPilot):
        """Test retrieving a non-existent unit returns 404."""
        with pytest.raises(ErrorNOTFOUND):
            client.units.get(serial_number="NONEXISTENT-UNIT-999")

    def test_get_unit_created_from(self, client: TofuPilot, procedure_id: str, auth_type: str):
        """Test unit includes the run that created it."""
        timestamp = str(int(time.time() * 1000000))
        serial_number = f"TEST-UNIT-CREATED-{timestamp}"
        
        # Create unit
        started_at, ended_at = get_random_test_dates()
        run_response = client.runs.create(
            outcome="PASS",
            procedure_id=procedure_id,
            serial_number=serial_number,
            part_number=f"TEST-PART-{timestamp}",
            started_at=started_at,
            ended_at=ended_at
        )
        assert_create_run_success(run_response)
        
        # Get the unit
        unit = client.units.get(serial_number=serial_number)
        
        # Verify created_from
        assert unit.created_from is not None
        assert unit.created_from.id == run_response.id  # type: ignore[union-attr]
        assert unit.created_from.outcome == "PASS"  # type: ignore[union-attr]
        assert unit.created_from.procedure is not None  # type: ignore[union-attr]