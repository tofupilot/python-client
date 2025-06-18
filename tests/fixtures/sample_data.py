"""Sample data and mock objects for testing."""

# Sample test data that can be used across different test files
TEST_SERIAL_NUMBERS = [
    "DEMO-001",
    "TEST-123",
    "SAMPLE-456"
]

TEST_RUN_IDS = [
    "test-run-123",
    "demo-run-456"
]

# Mock request bodies for different endpoints
SAMPLE_RUN_CREATE_BODY = {
    "unit_under_test": {
        "serial_number": "DEMO-001"
    },
    "outcome": "pass",
    "logs": []
}

SAMPLE_UPLOAD_INITIALIZE_BODY = {
    "serial_number": "DEMO-001",
    "filename": "test_log.txt"
}

SAMPLE_UNIT_UPDATE_PARENT_BODY = {
    "sub_units": [
        {"serial_number": "SUB-001"}
    ]
}