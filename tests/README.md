# Test Structure Documentation

## Directory Organization

```
tests/
├── conftest.py                    # Shared fixtures (client, api_key, base_url)
├── test_client_initialization.py  # Client setup and configuration tests
├── api/                           # API endpoint tests organized by service
│   ├── test_runs_api.py           # /v1/runs endpoints
│   ├── test_units_api.py          # /v1/units endpoints  
│   ├── test_uploads_api.py        # /v1/uploads endpoints
│   ├── test_streaming_api.py      # /v1/streaming endpoints
│   └── test_imports_api.py        # /v1/import endpoints
├── integration/                   # End-to-end workflow tests
└── fixtures/                     # Test data and sample files
    ├── sample_data.py             # Mock request/response data
    └── test_files/                # Sample files for upload tests
```

## Naming Convention

### Test Files
- **Format**: `test_{api_name}_api.py` 
- **Examples**: `test_runs_api.py`, `test_units_api.py`

### Test Methods
- **Format**: `test_{http_method}_{endpoint_description}_{scenario}`
- **Examples**: 
  - `test_get_runs_by_serial_success()`
  - `test_post_create_run_invalid_body_400()`
  - `test_delete_unit_not_found_404()`

### Test Classes
- **Format**: `Test{APIName}API`
- **Examples**: `TestRunsAPI`, `TestUnitsAPI`

## Running Tests

```bash
# Run all tests
pytest

# Run specific API tests
pytest tests/api/test_runs_api.py

# Run with coverage
pytest --cov=tofupilot

# Run only unit tests (no API calls)
pytest -m "not integration"

# Run with verbose output
pytest -v
```

## API Endpoints Coverage

| API Service | Endpoints | Test File |
|-------------|-----------|-----------|
| **Runs** | GET, POST, DELETE `/v1/runs` | `test_runs_api.py` |
| **Units** | DELETE, PATCH `/v1/units` | `test_units_api.py` |
| **Uploads** | POST `/v1/uploads/initialize`, `/v1/uploads/sync` | `test_uploads_api.py` |
| **Streaming** | GET `/v1/streaming` | `test_streaming_api.py` |
| **Imports** | POST `/v1/import` | `test_imports_api.py` |