"""Shared test configuration and fixtures."""

import os
import random
import tempfile
from pathlib import Path

import pytest
from tofupilot import TofuPilotClient


@pytest.fixture
def api_key():
    """Default API key for testing."""
    return os.getenv("TOFUPILOT_API_KEY", "76978854-ee7e-45ac-ba51-394103fdcc4a")


@pytest.fixture
def base_url():
    """Default base URL for testing."""
    return os.getenv("TOFUPILOT_BASE_URL", "http://localhost:3000")


@pytest.fixture
def client(api_key, base_url):
    """Authenticated TofuPilot client instance."""
    return TofuPilotClient(api_key=api_key, base_url=base_url)


@pytest.fixture
def test_serial_number():
    """Test serial number for demo data."""
    return "DEMO-001"


@pytest.fixture
def test_run_id():
    """Test run ID for demo data."""
    return "test-run-123"


@pytest.fixture
def random_serial_number():
    """Generate a random serial number for testing."""
    return f"QA-{random.randint(100000, 999999)}"


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def qa_examples_dir():
    """Get the QA examples directory."""
    return Path(__file__).parent.parent / "tmp" / "examples" / "qa"


@pytest.fixture(scope="session")
def qa_client_examples_dir():
    """Get the QA client examples directory (session-scoped)."""
    return Path(__file__).parent.parent / "tmp" / "examples" / "qa" / "client"


@pytest.fixture(scope="session") 
def qa_openhtf_examples_dir():
    """Get the QA OpenHTF examples directory (session-scoped)."""
    return Path(__file__).parent.parent / "tmp" / "examples" / "qa" / "openhtf"


@pytest.fixture
def sample_attachment_files(qa_client_examples_dir):
    """Get sample attachment files for testing."""
    files = {}
    
    # Temperature map PNG
    temp_map = qa_client_examples_dir / "create_run" / "with_attachments" / "data" / "temperature-map.png"
    if temp_map.exists():
        files["temperature_map"] = temp_map
    
    # Performance report PDF  
    perf_report = qa_client_examples_dir / "create_run" / "with_attachments" / "data" / "performance-report.pdf"
    if perf_report.exists():
        files["performance_report"] = perf_report
        
    # Oscilloscope JPEG
    scope_file = qa_client_examples_dir / "create_run_from_openhtf_report" / "with_attachments" / "data" / "oscilloscope.jpeg"
    if scope_file.exists():
        files["oscilloscope"] = scope_file
        
    # Sample text file
    sample_txt = qa_client_examples_dir / "create_run_from_openhtf_report" / "with_attachments" / "data" / "sample_file.txt"
    if sample_txt.exists():
        files["sample_text"] = sample_txt
    
    return files


@pytest.fixture
def basic_run_data(random_serial_number):
    """Standard run data for testing."""
    return {
        "serial_number": random_serial_number,
        "part_number": "PCB-001",
        "outcome": "PASS"
    }


def create_run_simple(client, serial_number: str, part_number: str, outcome: str = "PASS", **kwargs):
    """Helper function to create runs with simplified API for testing."""
    from tofupilot.openapi_client.models.run_create_body import RunCreateBody
    from tofupilot.openapi_client.models.run_create_body_unit_under_test import RunCreateBodyUnitUnderTest
    
    # Build the basic body
    unit_under_test = RunCreateBodyUnitUnderTest(
        serial_number=serial_number,
        part_number=part_number
    )
    
    body = RunCreateBody(
        unit_under_test=unit_under_test,
        run_passed=(outcome.upper() == "PASS"),
        procedure_id=kwargs.get("procedure_id", "default")
    )
    
    # Add optional fields
    if "procedure_version" in kwargs:
        body.procedure_version = kwargs["procedure_version"]
    if "started_at" in kwargs:
        body.started_at = kwargs["started_at"]
    if "duration_ms" in kwargs:
        # Convert ms to ISO 8601 duration
        seconds = kwargs["duration_ms"] / 1000
        body.duration = f"PT{seconds}S"
        
    return client.runs.create(body=body)


@pytest.fixture
def sample_measurements():
    """Sample measurements for testing."""
    return [
        {
            "name": "Voltage",
            "measured_value": 5.1,
            "units": "V",
            "lower_limit": 4.5,
            "upper_limit": 5.5
        },
        {
            "name": "Current",
            "measured_value": 0.8,
            "units": "A",
            "lower_limit": 0.5,
            "upper_limit": 1.0
        },
        {
            "name": "Temperature",
            "measured_value": 25.5,
            "units": "°C",
            "upper_limit": 85.0
        }
    ]


@pytest.fixture
def sample_phases(sample_measurements):
    """Sample phases for testing."""
    return [
        {
            "name": "Power Test",
            "outcome": "PASS",
            "measurements": sample_measurements[:2]  # Voltage and Current
        },
        {
            "name": "Temperature Test",
            "outcome": "PASS", 
            "measurements": [sample_measurements[2]]  # Temperature
        }
    ]