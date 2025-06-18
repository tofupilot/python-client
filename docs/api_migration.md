# TofuPilot Python Client API Migration Guide

This document provides a comprehensive mapping between the legacy API methods and the new dotted notation syntax.

## Overview

The TofuPilot Python client is transitioning from direct method calls to a structured dotted notation API. Legacy methods are still supported but will show deprecation warnings.

## API Method Mapping

### Runs API

#### Legacy → New Syntax

| Legacy Method | New Method | Status |
|---------------|------------|--------|
| `client.run_create(...)` | `client.runs.create(body)` | ⚠️ Deprecated |
| `client.create_run(...)` | `client.runs.create(body)` | ⚠️ Deprecated |
| `client.run_delete_single(run_id)` | `client.runs.delete(run_id)` | ⚠️ Deprecated |
| `client.delete_run(run_id)` | `client.runs.delete(run_id)` | ⚠️ Deprecated |
| `client.run_get_runs_by_serial_number(serial_number)` | `client.runs.get_by_serial(serial_number)` | ⚠️ Deprecated |
| `client.get_runs(serial_number)` | `client.runs.get_by_serial(serial_number)` | ⚠️ Deprecated |

#### Migration Examples

**Legacy:**
```python
# Old way
response = client.run_create(
    serial_number="TEST-001",
    part_number="PCB-001",
    outcome="PASS"
)
```

**New:**
```python
# New way
from tofupilot.openapi_client.models.run_create_body import RunCreateBody

body = RunCreateBody(
    unit_under_test={"serial_number": "TEST-001", "part_number": "PCB-001"},
    run_passed=True,
    procedure_id="default"
)
response = client.runs.create(body=body)
```

### Units API

| Legacy Method | New Method | Status |
|---------------|------------|--------|
| `client.unit_delete(serial_number)` | `client.units.delete(serial_number)` | ⚠️ Deprecated |
| `client.delete_unit(serial_number)` | `client.units.delete(serial_number)` | ⚠️ Deprecated |
| `client.unit_update_unit_parent(serial_number, body)` | `client.units.update_parent(serial_number, body)` | ⚠️ Deprecated |
| `client.update_unit_parent(serial_number, body)` | `client.units.update_parent(serial_number, body)` | ⚠️ Deprecated |

#### Migration Examples

**Legacy:**
```python
# Old way
response = client.unit_delete("TEST-001")
```

**New:**
```python
# New way
response = client.units.delete("TEST-001")
```

### Uploads API

| Legacy Method | New Method | Status |
|---------------|------------|--------|
| `client.upload_initialize(body)` | `client.uploads.initialize(body)` | ⚠️ Deprecated |
| `client.upload_sync_upload(body)` | `client.uploads.sync(body)` | ⚠️ Deprecated |

### Streaming API

| Legacy Method | New Method | Status |
|---------------|------------|--------|
| `client.streaming_get_streaming_token()` | `client.streaming.get_token()` | ⚠️ Deprecated |
| `client.get_streaming_token()` | `client.streaming.get_token()` | ⚠️ Deprecated |

### Imports API

| Legacy Method | New Method | Status |
|---------------|------------|--------|
| `client.run_create_from_file(file, importer)` | `client.imports.create_from_file(body)` | ⚠️ Deprecated |
| `client.create_run_from_file(file, importer)` | `client.imports.create_from_file(body)` | ⚠️ Deprecated |

#### Migration Examples

**Legacy:**
```python
# Old way
with open("test_data.json", "rb") as f:
    response = client.run_create_from_file(
        file=f.read(),
        importer="openhtf"
    )
```

**New:**
```python
# New way
from tofupilot.openapi_client.models.run_create_from_file_body import RunCreateFromFileBody

with open("test_data.json", "rb") as f:
    body = RunCreateFromFileBody(
        file=f.read(),
        importer="openhtf"
    )
    response = client.imports.create_from_file(body=body)
```

## Key Changes

### 1. Structured API Organization
- Methods are now organized under logical namespaces: `runs`, `units`, `uploads`, `streaming`, `imports`
- This provides better discoverability and organization

### 2. Explicit Model Usage
- The new API requires explicit use of model classes for request bodies
- This provides better type safety and validation
- IDE autocomplete and type hints work better

### 3. Consistent Parameter Handling
- All complex operations now use dedicated model classes
- Parameters are validated at the model level
- Better error messages for invalid parameters

## Convenience Parameter Mapping

The legacy methods often accepted convenience parameters that were automatically converted. Here's how they map:

### Run Creation Parameters

| Legacy Parameter | New Model Field | Notes |
|------------------|-----------------|-------|
| `serial_number` | `unit_under_test.serial_number` | Convenience wrapper |
| `part_number` | `unit_under_test.part_number` | Convenience wrapper |
| `outcome` | `run_passed` | "PASS" → `True`, "FAIL" → `False` |
| `phases` | `phases` | Direct mapping |
| `steps` | `steps` | Direct mapping (deprecated) |
| `procedure_version` | `procedure_version` | Direct mapping |
| `started_at` | `started_at` | Direct mapping |
| `duration_ms` | `duration` | Convert ms to ISO 8601 duration |
| `sub_units` | `sub_units` | Direct mapping |
| `logs` | `logs` | Direct mapping |

## Deprecation Timeline

- **v2.0.0**: Legacy methods added with deprecation warnings
- **v2.1.0**: Deprecation warnings become more prominent
- **v3.0.0**: Legacy methods will be removed (planned)

## Response Objects

Response objects remain the same between legacy and new APIs. The main difference is in how you call the methods, not what they return.

```python
# Both return the same response object
legacy_response = client.run_create(...)
new_response = client.runs.create(body)

# Both have the same attributes
print(legacy_response.parsed.id)
print(new_response.parsed.id)
```

## Migration Checklist

- [ ] Update imports to include model classes
- [ ] Replace direct method calls with dotted notation
- [ ] Update parameter passing to use model objects
- [ ] Test your migration with the new API
- [ ] Update any documentation or examples

## Getting Help

If you need help migrating your code:
1. Check this migration guide
2. Look at the updated examples in the `tests/integration/` directory
3. Use your IDE's autocomplete to discover new methods
4. Check the model classes in `tofupilot.openapi_client.models` for available fields