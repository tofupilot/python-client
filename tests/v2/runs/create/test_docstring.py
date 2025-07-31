"""Test docstring creation in runs."""

import uuid
from datetime import datetime, timedelta, timezone
from tofupilot.v2 import TofuPilot
from ...utils import assert_create_run_success


class TestDocstringCreation:

    def test_run_with_docstring(self, client: TofuPilot, procedure_id: str) -> None:
        """Test that runs with docstrings are properly created."""
        # Generate unique identifiers for this test
        unique_id = str(uuid.uuid4())[:8]
        SERIAL_NUMBER = f"TestUnit-Docstring-{unique_id}"
        PART_NUMBER = f"TestPart-Docstring-{unique_id}"
        REVISION_NUMBER = f"Rev-Docstring-{unique_id}"
        DOCSTRING = f"Test run with docstring - {unique_id}"
        
        OUTCOME = "PASS"
        NOW = datetime.now(timezone.utc)
        START_TIME = NOW - timedelta(minutes=5)
        END_TIME = NOW

        # Create run with docstring
        result = client.runs.create(
            serial_number=SERIAL_NUMBER,
            procedure_id=procedure_id,
            outcome=OUTCOME,
            part_number=PART_NUMBER,
            revision_number=REVISION_NUMBER,
            docstring=DOCSTRING,
            started_at=START_TIME,
            ended_at=END_TIME,
        )
        
        assert_create_run_success(result)
        
        # Get the created run details
        run = client.runs.get(id=result.id)
        
        # Verify docstring was saved properly
        assert run.docstring == DOCSTRING
        
        # Verify other basic properties
        assert run.outcome == OUTCOME
        assert run.procedure is not None
        assert run.procedure.id == procedure_id
        assert run.unit is not None
        assert run.unit.serial_number == SERIAL_NUMBER
        assert run.unit.part is not None
        assert run.unit.part.number == PART_NUMBER

    def test_run_without_docstring(self, client: TofuPilot, procedure_id: str) -> None:
        """Test that runs without docstrings are properly created."""
        # Generate unique identifiers for this test
        unique_id = str(uuid.uuid4())[:8]
        SERIAL_NUMBER = f"TestUnit-NoDocstring-{unique_id}"
        PART_NUMBER = f"TestPart-NoDocstring-{unique_id}"
        REVISION_NUMBER = f"Rev-NoDocstring-{unique_id}"
        
        OUTCOME = "PASS"
        NOW = datetime.now(timezone.utc)
        START_TIME = NOW - timedelta(minutes=5)
        END_TIME = NOW

        # Create run without docstring
        result = client.runs.create(
            serial_number=SERIAL_NUMBER,
            procedure_id=procedure_id,
            outcome=OUTCOME,
            part_number=PART_NUMBER,
            revision_number=REVISION_NUMBER,
            started_at=START_TIME,
            ended_at=END_TIME,
        )
        
        assert_create_run_success(result)
        
        # Get the created run details
        run = client.runs.get(id=result.id)
        
        # Verify docstring is None when not provided
        assert run.docstring is None
        
        # Verify other basic properties
        assert run.outcome == OUTCOME
        assert run.procedure is not None
        assert run.procedure.id == procedure_id
        assert run.unit is not None
        assert run.unit.serial_number == SERIAL_NUMBER
        assert run.unit.part is not None
        assert run.unit.part.number == PART_NUMBER

    def test_run_with_empty_docstring(self, client: TofuPilot, procedure_id: str) -> None:
        """Test that runs with empty docstrings are properly created."""
        # Generate unique identifiers for this test
        unique_id = str(uuid.uuid4())[:8]
        SERIAL_NUMBER = f"TestUnit-EmptyDocstring-{unique_id}"
        PART_NUMBER = f"TestPart-EmptyDocstring-{unique_id}"
        REVISION_NUMBER = f"Rev-EmptyDocstring-{unique_id}"
        
        OUTCOME = "PASS"
        NOW = datetime.now(timezone.utc)
        START_TIME = NOW - timedelta(minutes=5)
        END_TIME = NOW

        # Create run with empty docstring
        result = client.runs.create(
            serial_number=SERIAL_NUMBER,
            procedure_id=procedure_id,
            outcome=OUTCOME,
            part_number=PART_NUMBER,
            revision_number=REVISION_NUMBER,
            docstring="",
            started_at=START_TIME,
            ended_at=END_TIME,
        )
        
        assert_create_run_success(result)
        
        # Get the created run details
        run = client.runs.get(id=result.id)
        
        # Verify empty docstring was converted to None (empty strings are not stored)
        assert run.docstring is None
        
        # Verify other basic properties
        assert run.outcome == OUTCOME
        assert run.procedure is not None
        assert run.procedure.id == procedure_id
        assert run.unit is not None
        assert run.unit.serial_number == SERIAL_NUMBER
        assert run.unit.part is not None
        assert run.unit.part.number == PART_NUMBER

    def test_run_with_multiline_docstring(self, client: TofuPilot, procedure_id: str) -> None:
        """Test that runs with multiline docstrings are properly created."""
        # Generate unique identifiers for this test
        unique_id = str(uuid.uuid4())[:8]
        SERIAL_NUMBER = f"TestUnit-MultiDocstring-{unique_id}"
        PART_NUMBER = f"TestPart-MultiDocstring-{unique_id}"
        REVISION_NUMBER = f"Rev-MultiDocstring-{unique_id}"
        DOCSTRING = f"""Test run with multiline docstring - {unique_id}
        
This is a multiline docstring that spans
multiple lines to test proper handling
of newlines and formatting."""
        
        OUTCOME = "PASS"
        NOW = datetime.now(timezone.utc)
        START_TIME = NOW - timedelta(minutes=5)
        END_TIME = NOW

        # Create run with multiline docstring
        result = client.runs.create(
            serial_number=SERIAL_NUMBER,
            procedure_id=procedure_id,
            outcome=OUTCOME,
            part_number=PART_NUMBER,
            revision_number=REVISION_NUMBER,
            docstring=DOCSTRING,
            started_at=START_TIME,
            ended_at=END_TIME,
        )
        
        assert_create_run_success(result)
        
        # Get the created run details
        run = client.runs.get(id=result.id)
        
        # Verify multiline docstring was saved properly
        assert run.docstring == DOCSTRING
        
        # Verify other basic properties
        assert run.outcome == OUTCOME
        assert run.procedure is not None
        assert run.procedure.id == procedure_id
        assert run.unit is not None
        assert run.unit.serial_number == SERIAL_NUMBER
        assert run.unit.part is not None
        assert run.unit.part.number == PART_NUMBER