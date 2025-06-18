"""Simple test for creating runs via TofuPilotClient API."""

import random
import warnings


def assert_run_response(response):
    """Helper function to validate run response has valid status and ID."""
    assert response.status_code == 200
    assert hasattr(response, 'parsed')
    assert hasattr(response.parsed, 'id')
    assert response.parsed.id is not None

def test_create_run_legacy_deprecated(client, procedure_id):
    """Test creating a run using deprecated legacy create_run method."""
    random_digits = "".join([str(random.randint(0, 9)) for _ in range(5)])
    serial_number = f"00220D4K{random_digits}"
    
    # Capture deprecation warnings to verify create_run shows warning
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        
        response = client.create_run(
            serial_number=serial_number,
            part_number="PCB01",
            procedure_id=procedure_id,
            outcome="PASS"
        )
        
        # Verify that create_run raises a deprecation warning
        assert len(w) > 0, "Expected deprecation warning from create_run method"
        assert any("deprecated" in str(warning.message).lower() for warning in w), "Expected deprecation warning message"
    
    assert_run_response(response)


def test_create_run_new_api(client, procedure_id):
    """Test creating a run using new OpenAPI client syntax."""
    from tofupilot.openapi_client.models.run import Run
    
    random_digits = "".join([str(random.randint(0, 9)) for _ in range(5)])
    serial_number = f"00220D4K{random_digits}"
    
    # Create run using new API syntax
    response = client.runs.create(body=Run(
        part_number="PCB01",
        serial_number=serial_number,
        run_passed=True,
        procedure_id=procedure_id
    ))
    
    assert_run_response(response)