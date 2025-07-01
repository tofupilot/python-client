"""Tests for getting runs via TofuPilotClient API."""

import random
from datetime import datetime, timedelta


def test_get_runs_basic(client):
    """Test basic get_runs functionality."""
    response = client.runs.get_runs()
    
    assert response.status_code == 200
    assert hasattr(response, 'parsed')
    assert hasattr(response.parsed, 'data')
    assert hasattr(response.parsed, 'meta')
    assert hasattr(response.parsed, 'links')
    
    # Verify meta structure
    meta = response.parsed.meta
    assert hasattr(meta, 'total')
    assert hasattr(meta, 'limit')
    assert hasattr(meta, 'offset')
    assert isinstance(meta.total, int)
    assert isinstance(meta.limit, int)
    assert isinstance(meta.offset, int)
    
    # Verify links structure
    links = response.parsed.links
    assert hasattr(links, 'next')
    assert hasattr(links, 'prev')


def test_get_runs_with_filters(client):
    """Test get_runs with various filter parameters."""
    from tofupilot.openapi_client.models import Run, RunOutcome
    
    # Test with outcome filter
    response = client.runs.getRuns(Run(
        outcome=[RunOutcome.PASS, RunOutcome.FAIL],
        limit=10,
        offset=0
    ))
    
    assert response.status_code == 200
    assert len(response.parsed.data) <= 10
    
    # Verify all returned runs have the specified outcomes
    for run in response.parsed.data:
        assert run.outcome in [RunOutcome.PASS, RunOutcome.FAIL]


def test_get_runs_with_date_filters(client):
    """Test get_runs with date range filters."""
    # Get runs from the last 7 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    response = client.runs.get_runs(
        start_date_ms=int(start_date.timestamp() * 1000),
        end_date_ms=int(end_date.timestamp() * 1000),
        limit=20
    )
    
    assert response.status_code == 200
    assert hasattr(response.parsed, 'data')
    
    # Verify all returned runs are within the date range
    for run in response.parsed.data:
        run_date = run.started_at
        assert start_date <= run_date <= end_date


def test_get_runs_enriched_fields(client, procedure_id):
    """Test that get_runs returns enriched fields we added."""
    from tofupilot.openapi_client.models import Run, RunOutcome
    
    # First create a test run to ensure we have data
    random_digits = "".join([str(random.randint(0, 9)) for _ in range(5)])
    serial_number = f"TESTGET{random_digits}"
    
    create_response = client.runs.create(Run(
        serial_number=serial_number,
        part_number="PCB01",
        procedure_id=procedure_id,
        run_passed=True,
        outcome=RunOutcome.PASS
    ))
    
    assert create_response.status_code == 200
    run_id = create_response.parsed.id
    
    # Now get runs and verify enriched fields
    response = client.runs.get_runs(ids=[run_id])
    
    assert response.status_code == 200
    assert len(response.parsed.data) == 1
    
    run = response.parsed.data[0]
    
    # Verify basic fields
    assert hasattr(run, 'id')
    assert hasattr(run, 'outcome')
    assert hasattr(run, 'started_at')
    assert hasattr(run, 'created_at')
    assert hasattr(run, 'duration')
    
    # Verify enriched procedure fields
    if hasattr(run, 'procedure') and run.procedure:
        procedure = run.procedure
        assert hasattr(procedure, 'id')
        assert hasattr(procedure, 'name')
        assert hasattr(procedure, 'identifier')  # Enriched field
        assert procedure.identifier is not None
    
    # Verify enriched unit fields
    if hasattr(run, 'unit') and run.unit:
        unit = run.unit
        assert hasattr(unit, 'id')
        assert hasattr(unit, 'serial_number')
        
        # Verify enriched revision data
        if hasattr(unit, 'revision') and unit.revision:
            revision = unit.revision
            assert hasattr(revision, 'id')
            assert hasattr(revision, 'identifier')
            assert hasattr(revision, 'component')
            
            # Verify enriched component data
            if revision.component:
                component = revision.component
                assert hasattr(component, 'part_number')
                assert hasattr(component, 'name')
        
        # Verify batch data (may be null)
        if hasattr(unit, 'batch') and unit.batch:
            batch = unit.batch
            assert hasattr(batch, 'number')
    
    # Verify enriched creator fields
    if hasattr(run, 'created_by') and run.created_by:
        creator = run.created_by
        assert hasattr(creator, 'id')
        assert hasattr(creator, 'name')
        # Station identifier should be present for station creators
        if hasattr(creator, 'identifier'):
            assert creator.identifier is not None
    
    # Verify enriched phase fields
    if hasattr(run, 'phases') and run.phases:
        for phase in run.phases:
            assert hasattr(phase, 'id')
            assert hasattr(phase, 'name')
            assert hasattr(phase, 'outcome')
            assert hasattr(phase, 'started_at')
            assert hasattr(phase, 'duration')
            
            # Verify measurements if present
            if hasattr(phase, 'measurements') and phase.measurements:
                for measurement in phase.measurements:
                    assert hasattr(measurement, 'id')
                    assert hasattr(measurement, 'name')
                    assert hasattr(measurement, 'outcome')
                    # Check for measurement-specific fields based on type
                    if hasattr(measurement, 'value'):
                        # Numeric measurement
                        assert isinstance(measurement.value, (int, float))
                    elif hasattr(measurement, 'string_value'):
                        # String measurement
                        assert isinstance(measurement.string_value, str)
                    elif hasattr(measurement, 'bool_value'):
                        # Boolean measurement
                        assert isinstance(measurement.bool_value, bool)


def test_get_runs_with_exclusions(client):
    """Test get_runs with field exclusions."""
    # Test excluding specific fields
    response = client.runs.get_runs(
        exclude=['phases', 'attachments'],
        limit=5
    )
    
    assert response.status_code == 200
    
    # Verify excluded fields are not present
    for run in response.parsed.data:
        assert not hasattr(run, 'phases') or run.phases is None
        assert not hasattr(run, 'attachments') or run.attachments is None


def test_get_runs_sorting(client):
    """Test get_runs with different sorting options."""
    # Test descending sort by created_at (default)
    response_desc = client.runs.get_runs(
        sort='-created_at',
        limit=10
    )
    
    assert response_desc.status_code == 200
    
    # Test ascending sort by started_at
    response_asc = client.runs.get_runs(
        sort='started_at',
        limit=10
    )
    
    assert response_asc.status_code == 200
    
    # Verify sorting works (if we have multiple runs)
    if len(response_asc.parsed.data) > 1:
        dates = [run.started_at for run in response_asc.parsed.data]
        assert dates == sorted(dates)


def test_get_runs_pagination(client):
    """Test get_runs pagination functionality."""
    # Get first page
    response_page1 = client.runs.get_runs(
        limit=5,
        offset=0
    )
    
    assert response_page1.status_code == 200
    
    # Get second page
    response_page2 = client.runs.get_runs(
        limit=5,
        offset=5
    )
    
    assert response_page2.status_code == 200
    
    # Verify pagination links
    links = response_page1.parsed.links
    if response_page1.parsed.meta.total > 5:
        assert links.next is not None
        assert '/v1/runs?' in links.next
        assert 'offset=5' in links.next
    
    if response_page1.parsed.meta.offset > 0:
        assert links.prev is not None


def test_get_runs_by_procedure_id(client, procedure_id):
    """Test filtering runs by procedure ID."""
    response = client.runs.get_runs(
        procedure_id=[procedure_id],
        limit=10
    )
    
    assert response.status_code == 200
    
    # Verify all returned runs have the specified procedure ID
    for run in response.parsed.data:
        if hasattr(run, 'procedure') and run.procedure:
            assert run.procedure.id == procedure_id or run.procedure.identifier == procedure_id


def test_get_runs_by_unit_serial_number(client, procedure_id):
    """Test filtering runs by unit serial number."""
    from tofupilot.openapi_client.models import Run, RunOutcome
    
    # Create a test run with known serial number
    random_digits = "".join([str(random.randint(0, 9)) for _ in range(5)])
    serial_number = f"TESTSERIAL{random_digits}"
    
    create_response = client.runs.create(Run(
        serial_number=serial_number,
        part_number="PCB01",
        procedure_id=procedure_id,
        run_passed=True,
        outcome=RunOutcome.PASS
    ))
    
    assert create_response.status_code == 200
    
    # Now search for runs by this serial number
    response = client.runs.get_runs(
        unit_serial_numbers=[serial_number]
    )
    
    assert response.status_code == 200
    
    # Verify all returned runs have the specified serial number
    for run in response.parsed.data:
        if hasattr(run, 'unit') and run.unit:
            assert run.unit.serial_number == serial_number


def test_get_runs_empty_result(client):
    """Test get_runs with filters that return no results."""
    # Use a very specific filter that should return no results
    response = client.runs.get_runs(
        ids=["00000000-0000-0000-0000-000000000000"]  # Non-existent ID
    )
    
    assert response.status_code == 200
    assert len(response.parsed.data) == 0
    assert response.parsed.meta.total == 0