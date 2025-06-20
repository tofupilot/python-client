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
    from tofupilot.openapi_client.models import RunOutcome
    random_digits = "".join([str(random.randint(0, 9)) for _ in range(5)])
    serial_number = f"00220D4K{random_digits}"
    
    # Capture deprecation warnings to verify create_run shows warning
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        
        response = client.create_run(
            serial_number=serial_number,
            part_number="PCB01",
            procedure_id=procedure_id,
            outcome=RunOutcome.PASS
        )
        
        # Verify that create_run raises a deprecation warning
        assert len(w) > 0, "Expected deprecation warning from create_run method"
        assert any("deprecated" in str(warning.message).lower() for warning in w), "Expected deprecation warning message"
    
    assert_run_response(response)

def test_create_run_new_api(client, procedure_id):
    """Test creating a run using new OpenAPI client syntax."""
    from tofupilot.openapi_client.models import Run, RunOutcome
    
    random_digits = "".join([str(random.randint(0, 9)) for _ in range(5)])
    serial_number = f"00220D4K{random_digits}"
    
    # Create run using new API syntax - now with custom names!
    response = client.runs.create(Run(
        serial_number=serial_number,
        part_number="PCB01",
        procedure_id=procedure_id,
        run_passed=True,
        outcome=RunOutcome.PASS
    ))
    
    assert_run_response(response)


def test_create_run_with_enum_examples(client, procedure_id):
    """Examples of using the auto-generated RunOutcome enum with custom names."""
    from tofupilot.openapi_client.models import Run, RunOutcome
    
    # Example 1: Using enum for PASS
    response_pass = client.runs.create(Run(
        serial_number=f"TEST-PASS-{random.randint(10000, 99999)}",
        part_number="PCB01",
        procedure_id=procedure_id,
        run_passed=True,
        outcome=RunOutcome.PASS  # Clean enum name!
    ))
    assert_run_response(response_pass)
    
    # Example 2: Using enum for FAIL  
    response_fail = client.runs.create(Run(
        serial_number=f"TEST-FAIL-{random.randint(10000, 99999)}",
        part_number="PCB01",
        procedure_id=procedure_id,
        run_passed=False,
        outcome=RunOutcome.FAIL  # Clean enum name!
    ))
    assert_run_response(response_fail)
    
    # Example 3: Using enum for ERROR
    response_error = client.runs.create(Run(
        serial_number=f"TEST-ERROR-{random.randint(10000, 99999)}",
        part_number="PCB01",
        procedure_id=procedure_id,
        run_passed=False,
        outcome=RunOutcome.ERROR  # Clean enum name!
    ))
    assert_run_response(response_error)
    
    # Example 4: Using enum for TIMEOUT
    response_timeout = client.runs.create(Run(
        serial_number=f"TEST-TIMEOUT-{random.randint(10000, 99999)}",
        part_number="PCB01",
        procedure_id=procedure_id,
        run_passed=False,
        outcome=RunOutcome.TIMEOUT  # Use enum instead of string
    ))
    assert_run_response(response_timeout)
    
    # Custom class names and real enums provide these benefits:
    # 1. Cleaner imports: Run instead of RunCreateBody
    # 2. Cleaner enum names: RunOutcome instead of RunCreateBodyOutcome
    # 3. Auto-completion in IDE shows all available values
    # 4. Type safety prevents invalid values
    # 5. Prevents typos
    # 6. Must use enum values (strings no longer work with literal_enums: false)
    # Available enum values:
    # - RunOutcome.PASS, RunOutcome.FAIL, RunOutcome.ERROR
    # - RunOutcome.ABORTED, RunOutcome.RUNNING, RunOutcome.TIMEOUT