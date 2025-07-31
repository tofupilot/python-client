"""Test revision GET endpoint."""

import time
import pytest
from datetime import datetime, timezone
from tofupilot.v2 import TofuPilot
from tofupilot.v2.errors import ErrorNOTFOUND
from ...utils import assert_create_run_success, get_random_test_dates
from ..utils import assert_create_revision_success
from ...parts.utils import assert_create_part_success


class TestGetRevision:
    """Test retrieving individual revisions by ID."""

    def test_get_existing_revision(self, client: TofuPilot):
        """Test retrieving an existing revision by its ID."""
        # Create part first
        part_number = f"TEST-PART-REV-GET-{int(time.time() * 1000)}"
        part_response = client.parts.create(
            number=part_number,
            name="Part for Revision GET"
        )
        assert_create_part_success(part_response)
        
        # Create revision for the part
        revision_response = client.parts.revisions.create(part_number=part_number
        , number="REV-A")
        assert_create_revision_success(revision_response)
        
        # Get the revision by part number and revision number
        revision = client.parts.revisions.get(part_number=part_number, revision_number="REV-A")
        
        # Verify response
        assert revision.id == revision_response.id
        assert revision.number == "REV-A"
        assert revision.part is not None
        assert revision.part.id == part_response.id
        assert revision.part.number == part_number
        assert revision.part.name == "Part for Revision GET"

    def test_get_revision_with_units(self, client: TofuPilot, procedure_id: str):
        """Test retrieving a revision includes its units."""
        # Create part
        part_number = f"TEST-PART-REV-UNITS-{int(time.time() * 1000)}"
        part_response = client.parts.create(
            number=part_number,
            name="Part with Units"
        )
        assert_create_part_success(part_response)
        
        # Create revision
        revision_response = client.parts.revisions.create(part_number=part_number
        , number="REV-B")
        assert_create_revision_success(revision_response)
        
        # Create units for this revision
        unit_count = 3
        for i in range(unit_count):
            started_at, ended_at = get_random_test_dates()
            run = client.runs.create(
                outcome="PASS",
                procedure_id=procedure_id,
                serial_number=f"UNIT-REV-{int(time.time() * 1000)}-{i:03d}",
                part_number=part_number,
                revision_number="REV-B",
                started_at=started_at,
                ended_at=ended_at
            )
            assert_create_run_success(run)
        
        # Get the revision
        revision = client.parts.revisions.get(part_number=part_number, revision_number="REV-B")
        
        # Verify units
        assert hasattr(revision, 'units')
        assert len(revision.units) == unit_count
        
        # Verify unit details
        for unit in revision.units:
            assert unit.id is not None
            assert unit.serial_number is not None
            assert hasattr(unit, 'children_count')
            assert hasattr(unit, 'runs')

    def test_get_revision_with_unit_runs(self, client: TofuPilot, procedure_id: str):
        """Test revision includes run information for its units."""
        # Create part
        part_number = f"TEST-PART-REV-RUNS-{int(time.time() * 1000)}"
        part_response = client.parts.create(
            number=part_number,
            name="Part with Run History"
        )
        assert_create_part_success(part_response)
        
        # Create revision
        revision_response = client.parts.revisions.create(part_number=part_number
        , number="REV-C")
        assert_create_revision_success(revision_response)
        
        # Create unit with multiple runs
        serial_number = f"UNIT-WITH-RUNS-{int(time.time() * 1000)}"
        for i in range(3):
            # Use different duration for variety
            started_at, ended_at = get_random_test_dates(duration_minutes=5 + i)
            run = client.runs.create(
                outcome="PASS" if i == 0 else "FAIL",
                procedure_id=procedure_id,
                serial_number=serial_number,
                part_number=part_number,
                revision_number="REV-C",
                started_at=started_at,
                ended_at=ended_at
            )
            assert_create_run_success(run)
        
        # Get the revision
        revision = client.parts.revisions.get(part_number=part_number, revision_number="REV-C")
        
        # Find the unit
        unit = next((u for u in revision.units if u.serial_number == serial_number), None)
        assert unit is not None
        
        # Verify runs
        assert len(unit.runs) >= 3
        for run in unit.runs:
            assert run.id is not None
            assert run.started_at is not None
            assert run.outcome in ["PASS", "FAIL"]
            if run.procedure:
                assert run.procedure.name is not None

    def test_get_revision_with_image(self, client: TofuPilot):
        """Test revision includes image information if present."""
        # Create part
        part_number = f"TEST-PART-REV-IMAGE-{int(time.time() * 1000)}"
        part_response = client.parts.create(
            number=part_number,
            name="Part with Image"
        )
        assert_create_part_success(part_response)
        
        # Create revision
        revision_response = client.parts.revisions.create(part_number=part_number
        , number="REV-IMG")
        assert_create_revision_success(revision_response)
        
        # Get the revision
        revision = client.parts.revisions.get(part_number=part_number, revision_number="REV-IMG")
        
        # Verify image field exists (may be null)
        assert hasattr(revision, 'image')

    def test_get_nonexistent_revision(self, client: TofuPilot):
        """Test retrieving a non-existent revision returns error."""
        fake_part_number = "FAKE-PART-12345"
        fake_revision_number = "FAKE-REV-12345"
        # Note: The API should return 404 error for non-existent revisions
        with pytest.raises(ErrorNOTFOUND):
            client.parts.revisions.get(part_number=fake_part_number, revision_number=fake_revision_number)