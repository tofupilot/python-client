"""Test case-insensitive behavior of upsert operations."""
import os
import pytest
import uuid
from datetime import datetime, timedelta, timezone
from tofupilot.v2 import TofuPilot


@pytest.mark.parametrize("client", ["user", "station"], indirect=True)
class TestCaseInsensitiveUpserts:
    """Test that upserts are case-insensitive for normalized fields."""

    @pytest.fixture
    def procedure_id(self, client: TofuPilot, auth_type: str) -> str:
        """Create a procedure for testing."""
        if auth_type == "station":
            # Stations cannot create procedures, use environment variable
            procedure_id = os.environ.get("TOFUPILOT_PROCEDURE_ID")
            if not procedure_id:
                pytest.skip("Station tests require TOFUPILOT_PROCEDURE_ID environment variable")
            return procedure_id
        else:
            procedure = client.procedures.create(
                name=f"Test Procedure {uuid.uuid4()}"
            )
            return procedure.id

    def test_batch_upsert_case_insensitive(self, client: TofuPilot, procedure_id: str):
        """Test that batch upserts are case-insensitive."""
        batch_number = f"BATCH-{uuid.uuid4()}"
        now = datetime.now(timezone.utc)
        
        # Create run with uppercase batch number
        run1 = client.runs.create(
            serial_number=f"unit-{uuid.uuid4()}",
            part_number=f"part-{uuid.uuid4()}",
            batch_number=batch_number.upper(),
            procedure_id=procedure_id,
            outcome="PASS",
            started_at=now - timedelta(minutes=10),
            ended_at=now - timedelta(minutes=9)
        )
        
        # Create another run with lowercase batch number - should use existing batch
        run2 = client.runs.create(
            serial_number=f"unit-{uuid.uuid4()}",
            part_number=f"part-{uuid.uuid4()}",
            batch_number=batch_number.lower(),
            procedure_id=procedure_id,
            outcome="PASS",
            started_at=now - timedelta(minutes=8),
            ended_at=now - timedelta(minutes=7)
        )
        
        # Get run details to verify batch IDs
        run1_details = client.runs.get(id=run1.id)
        run2_details = client.runs.get(id=run2.id)
        
        # Verify both runs reference the same batch
        assert run1_details.unit.batch is not None
        assert run2_details.unit.batch is not None
        assert run1_details.unit.batch.id == run2_details.unit.batch.id
        
        # Also test with mixed case and whitespace
        run3 = client.runs.create(
            serial_number=f"unit-{uuid.uuid4()}",
            part_number=f"part-{uuid.uuid4()}",
            batch_number=f"  {batch_number.title()}  ",  # With spaces and title case
            procedure_id=procedure_id,
            outcome="PASS",
            started_at=now - timedelta(minutes=6),
            ended_at=now - timedelta(minutes=5)
        )
        
        run3_details = client.runs.get(id=run3.id)
        assert run3_details.unit.batch is not None
        assert run1_details.unit.batch.id == run3_details.unit.batch.id

    def test_part_upsert_case_insensitive(self, client: TofuPilot, procedure_id: str):
        """Test that part upserts are case-insensitive."""
        part_number = f"PART-{uuid.uuid4()}"
        now = datetime.now(timezone.utc)
        
        # Create run with uppercase part number
        run1 = client.runs.create(
            serial_number=f"unit-{uuid.uuid4()}",
            part_number=part_number.upper(),
            procedure_id=procedure_id,
            outcome="PASS",
            started_at=now - timedelta(minutes=10),
            ended_at=now - timedelta(minutes=9)
        )
        
        # Create another run with lowercase part number - should use existing part
        run2 = client.runs.create(
            serial_number=f"unit-{uuid.uuid4()}",
            part_number=part_number.lower(),
            procedure_id=procedure_id,
            outcome="PASS",
            started_at=now - timedelta(minutes=8),
            ended_at=now - timedelta(minutes=7)
        )
        
        # Get run details to verify part IDs
        run1_details = client.runs.get(id=run1.id)
        run2_details = client.runs.get(id=run2.id)
        
        # Verify both runs reference the same part
        assert run1_details.unit.part.id == run2_details.unit.part.id
        
        # Also test with mixed case and whitespace
        run3 = client.runs.create(
            serial_number=f"unit-{uuid.uuid4()}",
            part_number=f"  {part_number.title()}  ",  # With spaces and title case
            procedure_id=procedure_id,
            outcome="PASS",
            started_at=now - timedelta(minutes=6),
            ended_at=now - timedelta(minutes=5)
        )
        
        run3_details = client.runs.get(id=run3.id)
        assert run1_details.unit.part.id == run3_details.unit.part.id

    def test_unit_upsert_case_insensitive(self, client: TofuPilot, procedure_id: str):
        """Test that unit upserts are case-insensitive."""
        serial_number = f"UNIT-{uuid.uuid4()}"
        part_number = f"part-{uuid.uuid4()}"
        now = datetime.now(timezone.utc)
        
        # Create run with uppercase serial number
        run1 = client.runs.create(
            serial_number=serial_number.upper(),
            part_number=part_number,
            procedure_id=procedure_id,
            outcome="PASS",
            started_at=now - timedelta(minutes=10),
            ended_at=now - timedelta(minutes=9)
        )
        
        # Create another run with lowercase serial number - should use existing unit
        run2 = client.runs.create(
            serial_number=serial_number.lower(),
            part_number=part_number,
            procedure_id=procedure_id,
            outcome="FAIL",
            started_at=now - timedelta(minutes=8),
            ended_at=now - timedelta(minutes=7)
        )
        
        # Get run details to verify unit IDs
        run1_details = client.runs.get(id=run1.id)
        run2_details = client.runs.get(id=run2.id)
        
        # Verify both runs reference the same unit
        assert run1_details.unit.id == run2_details.unit.id
        
        # Also test with mixed case and whitespace
        run3 = client.runs.create(
            serial_number=f"  {serial_number.title()}  ",  # With spaces and title case
            part_number=part_number,
            procedure_id=procedure_id,
            outcome="ERROR",
            started_at=now - timedelta(minutes=6),
            ended_at=now - timedelta(minutes=5)
        )
        
        run3_details = client.runs.get(id=run3.id)
        assert run1_details.unit.id == run3_details.unit.id

    def test_revision_upsert_case_insensitive(self, client: TofuPilot, procedure_id: str):
        """Test that revision upserts are case-insensitive."""
        part_number = f"part-{uuid.uuid4()}"
        revision_number = f"REV-{uuid.uuid4()}"
        now = datetime.now(timezone.utc)
        
        # Create run with uppercase revision number
        run1 = client.runs.create(
            serial_number=f"unit-{uuid.uuid4()}",
            part_number=part_number,
            revision_number=revision_number.upper(),
            procedure_id=procedure_id,
            outcome="PASS",
            started_at=now - timedelta(minutes=10),
            ended_at=now - timedelta(minutes=9)
        )
        
        # Create another run with lowercase revision number - should use existing revision
        run2 = client.runs.create(
            serial_number=f"unit-{uuid.uuid4()}",
            part_number=part_number,
            revision_number=revision_number.lower(),
            procedure_id=procedure_id,
            outcome="PASS",
            started_at=now - timedelta(minutes=8),
            ended_at=now - timedelta(minutes=7)
        )
        
        # Get run details to verify revision IDs
        run1_details = client.runs.get(id=run1.id)
        run2_details = client.runs.get(id=run2.id)
        
        # Verify both runs reference the same revision
        assert run1_details.unit.part.revision.id == run2_details.unit.part.revision.id
        
        # Also test with mixed case and whitespace
        run3 = client.runs.create(
            serial_number=f"unit-{uuid.uuid4()}",
            part_number=part_number,
            revision_number=f"  {revision_number.title()}  ",  # With spaces and title case
            procedure_id=procedure_id,
            outcome="PASS",
            started_at=now - timedelta(minutes=6),
            ended_at=now - timedelta(minutes=5)
        )
        
        run3_details = client.runs.get(id=run3.id)
        assert run1_details.unit.part.revision.id == run3_details.unit.part.revision.id

    def test_procedure_version_upsert_case_insensitive(self, client: TofuPilot, procedure_id: str):
        """Test that procedure version upserts are case-insensitive."""
        version_tag = f"v{str(uuid.uuid4()).replace('-', '')[:8]}"
        now = datetime.now(timezone.utc)
        
        # Create run with lowercase version tag (procedure versions use lowercase constraint)
        run1 = client.runs.create(
            serial_number=f"unit-{uuid.uuid4()}",
            part_number=f"part-{uuid.uuid4()}",
            procedure_id=procedure_id,
            procedure_version=version_tag.lower(),
            outcome="PASS",
            started_at=now - timedelta(minutes=10),
            ended_at=now - timedelta(minutes=9)
        )
        
        # Create another run with uppercase version tag - should be normalized to lowercase
        run2 = client.runs.create(
            serial_number=f"unit-{uuid.uuid4()}",
            part_number=f"part-{uuid.uuid4()}",
            procedure_id=procedure_id,
            procedure_version=version_tag.upper(),
            outcome="PASS",
            started_at=now - timedelta(minutes=8),
            ended_at=now - timedelta(minutes=7)
        )
        
        # Get run details to verify procedure version IDs
        run1_details = client.runs.get(id=run1.id)
        run2_details = client.runs.get(id=run2.id)
        
        # Verify both runs reference the same procedure version
        assert run1_details.procedure.version is not None
        assert run2_details.procedure.version is not None
        assert run1_details.procedure.version.id == run2_details.procedure.version.id
        
        # Also test with mixed case and whitespace
        run3 = client.runs.create(
            serial_number=f"unit-{uuid.uuid4()}",
            part_number=f"part-{uuid.uuid4()}",
            procedure_id=procedure_id,
            procedure_version=f"  {version_tag.title()}  ",  # With spaces and title case
            outcome="PASS",
            started_at=now - timedelta(minutes=6),
            ended_at=now - timedelta(minutes=5)
        )
        
        run3_details = client.runs.get(id=run3.id)
        assert run3_details.procedure.version is not None
        assert run1_details.procedure.version.id == run3_details.procedure.version.id

    def test_combined_case_insensitive_upserts(self, client: TofuPilot, procedure_id: str):
        """Test that all upserts work together with case variations."""
        # Base identifiers
        part_number = f"PART-{uuid.uuid4()}"
        revision_number = f"REV-{uuid.uuid4()}"
        batch_number = f"BATCH-{uuid.uuid4()}"
        serial_number = f"UNIT-{uuid.uuid4()}"
        version_tag = f"v{str(uuid.uuid4()).replace('-', '')[:8]}"
        now = datetime.now(timezone.utc)
        
        # Create first run with all uppercase
        run1 = client.runs.create(
            serial_number=serial_number.upper(),
            part_number=part_number.upper(),
            revision_number=revision_number.upper(),
            batch_number=batch_number.upper(),
            procedure_id=procedure_id,
            procedure_version=version_tag.lower(),  # Procedure versions must be lowercase
            outcome="PASS",
            started_at=now - timedelta(minutes=10),
            ended_at=now - timedelta(minutes=9)
        )
        
        # Create second run with all lowercase and whitespace
        run2 = client.runs.create(
            serial_number=f"  {serial_number.lower()}  ",
            part_number=f"  {part_number.lower()}  ",
            revision_number=f"  {revision_number.lower()}  ",
            batch_number=f"  {batch_number.lower()}  ",
            procedure_id=procedure_id,
            procedure_version=f"  {version_tag.upper()}  ",  # Will be normalized
            outcome="FAIL",
            started_at=now - timedelta(minutes=8),
            ended_at=now - timedelta(minutes=7)
        )
        
        # Get run details to verify all entities were matched
        run1_details = client.runs.get(id=run1.id)
        run2_details = client.runs.get(id=run2.id)
        
        # Verify all entities were matched
        assert run1_details.unit.id == run2_details.unit.id
        assert run1_details.unit.part.id == run2_details.unit.part.id
        assert run1_details.unit.part.revision.id == run2_details.unit.part.revision.id
        assert run1_details.unit.batch is not None
        assert run2_details.unit.batch is not None
        assert run1_details.unit.batch.id == run2_details.unit.batch.id
        assert run1_details.procedure.version is not None
        assert run2_details.procedure.version is not None
        assert run1_details.procedure.version.id == run2_details.procedure.version.id