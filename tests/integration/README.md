# Integration Test Suite

This directory contains comprehensive integration tests for the TofuPilot Python client, converted from the original QA scripts in the `tmp/examples/qa/` directory.

## Overview

The integration tests are organized into several test modules, each covering different aspects of the TofuPilot API:

### Test Modules

1. **`test_create_run.py`** - Run creation functionality
   - Basic run creation
   - FPY (First Pass Yield) testing
   - Timing and duration tests
   - Sub-unit management
   - Phase and measurement handling
   - File attachments
   - All measurement types (numeric, string, boolean, JSON, null)

2. **`test_crud_operations.py`** - CRUD operations
   - Delete run functionality
   - Delete unit functionality 
   - Get runs by serial number
   - Get runs with attachments
   - Update unit relationships

3. **`test_legacy_steps.py`** - Legacy steps API
   - Required step parameters
   - Optional step parameters
   - Advanced multi-step scenarios

4. **`test_openhtf_import.py`** - OpenHTF report import
   - Basic OpenHTF JSON import
   - OpenHTF import with attachments

5. **`test_openhtf_integration.py`** - OpenHTF framework integration
   - Comprehensive feature testing
   - Multi-dimensional measurements
   - Logging integration
   - File attachments
   - Streaming and batch modes

## Test Organization

### Markers

Tests are organized using pytest markers for easy filtering:

- `@pytest.mark.integration` - All integration tests (requires API access)
- `@pytest.mark.create_run` - Run creation tests
- `@pytest.mark.crud` - CRUD operation tests
- `@pytest.mark.openhtf` - OpenHTF integration tests
- `@pytest.mark.attachments` - Tests involving file attachments
- `@pytest.mark.measurements` - Tests focusing on measurement data
- `@pytest.mark.legacy` - Tests for legacy API features
- `@pytest.mark.slow` - Slow-running tests

### Test Data

Test data files are preserved from the original QA examples in:
```
tmp/examples/qa/client/*/data/
tmp/examples/qa/openhtf/*/data/
```

These include:
- `temperature-map.png` - Sample PNG image
- `performance-report.pdf` - Sample PDF document
- `oscilloscope.jpeg` - Sample JPEG image
- `sample_file.txt` - Sample text file

## Running Tests

### Prerequisites

1. TofuPilot server running (default: `http://localhost:3000`)
2. Valid API key (default test key provided in fixtures)
3. Virtual environment activated

### Running All Integration Tests

```bash
# Run all integration tests
pytest tests/integration/ -v

# Run with specific markers
pytest tests/integration/ -m "create_run" -v
pytest tests/integration/ -m "openhtf" -v
pytest tests/integration/ -m "attachments" -v
```

### Running Specific Test Categories

```bash
# Run only CRUD tests
pytest tests/integration/test_crud_operations.py -v

# Run only OpenHTF integration tests
pytest tests/integration/test_openhtf_integration.py -v

# Run legacy API tests
pytest tests/integration/ -m "legacy" -v
```

### Environment Configuration

Tests use environment variables for configuration:

```bash
export TOFUPILOT_API_KEY="your-api-key"
export TOFUPILOT_BASE_URL="http://localhost:3000"
```

If not set, tests use default values from `conftest.py`.

## Test Coverage

The test suite covers all original QA script functionality:

### Client API Tests (21 original scripts → 18 test functions)
- ✅ Basic run creation
- ✅ FPY testing (multiple runs same serial)
- ✅ Custom start times and durations
- ✅ Sub-unit management (single and multiple)
- ✅ All measurement types
- ✅ File attachments (PNG, PDF)
- ✅ OpenHTF report import
- ✅ CRUD operations (delete, get, update)
- ✅ Legacy steps API

### OpenHTF Integration Tests (8 original scripts → 8 test functions)
- ✅ Comprehensive feature testing
- ✅ Multi-dimensional measurements
- ✅ Time-series data
- ✅ Logging levels
- ✅ File attachments
- ✅ Streaming vs batch modes
- ✅ Procedure versioning
- ✅ Serial number parsing

### Key Features Tested

1. **Measurement Types:**
   - Numeric with limits (voltage, current, temperature, percentages)
   - String measurements (firmware versions, status)
   - Boolean measurements (connection status, error flags)
   - JSON/Object measurements (configuration data)
   - Null/empty measurements
   - Multi-dimensional arrays (time series, frequency domain)

2. **Data Structures:**
   - Phases with outcomes (PASS/FAIL/CONTINUE/STOP)
   - Steps with timing and measurements (legacy format)
   - Sub-units and unit relationships
   - File attachments with proper content types

3. **Timing and Duration:**
   - Custom start times
   - Duration measurement
   - Time-series data collection

4. **Error Scenarios:**
   - Failing measurements
   - Out-of-limit values
   - Communication errors
   - System failures

## Fixtures and Utilities

### Core Fixtures (from `conftest.py`)
- `client` - Authenticated TofuPilotClient instance
- `random_serial_number` - Generate unique serial numbers
- `sample_attachment_files` - Access to test data files
- `basic_run_data` - Standard run creation data
- `sample_measurements` - Common measurement patterns
- `sample_phases` - Standard phase structures

### Test Data Fixtures
- `test_data_dir` - Access to QA examples directory
- `qa_client_examples_dir` - Client test data location
- `qa_openhtf_examples_dir` - OpenHTF test data location

## Migration from QA Scripts

The conversion from original QA scripts to pytest tests maintains:

1. **All test scenarios** - Every original test case is preserved
2. **Original test data** - All data files and attachments preserved
3. **Test patterns** - Similar test flow and validation
4. **API coverage** - Complete coverage of all API endpoints

### Key Improvements

1. **Pytest integration** - Standard Python testing framework
2. **Fixtures and reusability** - Shared test setup and data
3. **Parametrization** - Easy to add test variations
4. **Markers** - Flexible test filtering and organization
5. **Better error reporting** - Detailed failure information
6. **CI/CD ready** - Easy integration with automated testing

## Maintenance

### Adding New Tests

1. Follow existing naming conventions: `test_<functionality>_<scenario>`
2. Use appropriate markers for categorization
3. Leverage existing fixtures for common setup
4. Include docstrings describing test purpose
5. Preserve any test data files in appropriate directories

### Updating Tests

When API changes occur:
1. Update client method calls in affected tests
2. Verify test data compatibility
3. Update fixtures if data structures change
4. Run full test suite to verify compatibility