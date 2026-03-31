## V1 Test Scenarios

> **Status convention:**
>
> - `✅ Asserted` — scenario runs AND outcome is explicitly asserted on the created run
> - `🔄 Exercised` — scenario runs but outcome is not asserted (smoke test / no-crash check)
> - `❌ Untested` — no test covers this scenario

> **Note:** An autouse `no_error_logs` fixture in `test_from_openhtf.py` asserts zero ERROR-level log records for every test in `TestCreateRunFromOpenHTF`. This guards against silent failures but does not verify run properties.

### 1. End-to-End Workflows

| Scenario                                         | Status       | File                     | Function Name                        | Details                                                                                              |
| ------------------------------------------------ | ------------ | ------------------------ | ------------------------------------ | ---------------------------------------------------------------------------------------------------- |
| Full test with all measurement types             | ✅ Asserted  | `test_all_the_things.py` | `test_all_the_things`                | Regex, range, dimensions, marginals, attachments — phases, values, and validators asserted           |
| Teardown phase executes after test               | ✅ Asserted  | `test_all_the_things.py` | `test_all_the_things`                | PhaseGroup.with_teardown runs teardown; phase present and PASS asserted                              |
| Cross-phase data integrity                       | ✅ Asserted  | `test_all_the_things.py` | `test_all_the_things`                | `analysis` phase re-reads measurements and attachments set by earlier phases                         |
| JSON output callback generates file              | 🔄 Exercised | `test_all_the_things.py` | `test_all_the_things`                | OutputToJSON callback added but file existence is not asserted                                       |
| Streaming mode                                   | ✅ Asserted  | `test_all_the_things.py` | `test_all_the_things` (parametrized) | Runs with `stream=True`; full assertions applied                                                     |
| Non-streaming mode                               | ✅ Asserted  | `test_all_the_things.py` | `test_all_the_things` (parametrized) | Runs with `stream=False`; full assertions applied                                                    |
| Generic PCB test procedure                       | ✅ Asserted  | `test_generic.py`        | `test_generic`                       | Firmware, button, voltage, overcurrent, efficiency, visual ctrl. Deterministic values — always PASS. |
| Run with part number, revision, and batch number | ✅ Asserted  | `test_generic.py`        | `test_generic`                       | Asserts all three fields on created run                                                              |

### 2. Run Creation from OpenHTF Reports

| Scenario                                          | Status       | File                   | Function Name                                  | Details                                                                                         |
| ------------------------------------------------- | ------------ | ---------------------- | ---------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| Basic OpenHTF run creation                        | 🔄 Exercised | `test_from_openhtf.py` | `test_basic_openhtf_run_creation`              | Single power-on phase → run created; no run property assertions                                 |
| Run creation with file attachments                | 🔄 Exercised | `test_from_openhtf.py` | `test_openhtf_run_creation_with_attachments`   | Text file + JPEG image attached; no run property assertions                                     |
| Run creation with multi-dimensional measurements  | 🔄 Exercised | `test_from_openhtf.py` | `test_openhtf_multidimensional_measurements`   | Power time series, temperature profiles, frequency response; no run property assertions         |
| Import from pre-existing OpenHTF JSON report file | ✅ Asserted  | `test_from_openhtf.py` | `test_create_run_from_openhtf_json_report`     | JSON file → `create_run_from_openhtf_report()` → run ID, serial_number, part_number asserted    |
| Run creation with `upload` callback directly      | 🔄 Exercised | `test_from_openhtf.py` | `test_upload_callback_without_context_manager` | `upload` class as output callback without TofuPilot context manager; no run property assertions |

### 3. Measurements

| Scenario                                         | Status       | File                         | Function Name             | Details                                                                                                               |
| ------------------------------------------------ | ------------ | ---------------------------- | ------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| Multi-dimensional measurements (1D, 2D, 3D)      | 🔄 Exercised | `test_multi_dimensions.py`   | `test_multi_dimensions`   | Voltage over time, sinus, negative axes, current/voltage/ohm; phase names asserted but measurement values have a TODO |
| Multiple measurement types in single run         | ✅ Asserted  | `test_multi_measurements.py` | `test_multi_measurements` | String, boolean, phase result, numeric with limits, dimensioned; phase names and outcomes asserted                    |
| Deliberately failing measurements → FAIL outcome | ✅ Asserted  | `test_multi_measurements.py` | `test_multi_measurements` | Wrong types trigger per-phase FAIL, others remain PASS                                                                |
| Measurements with range validators               | ✅ Asserted  | `test_all_the_things.py`     | `test_all_the_things`     | `in_range`, `matches_regex`, `equals` — validators presence asserted on run                                           |
| Measurements with marginal arguments             | ✅ Asserted  | `test_all_the_things.py`     | `test_all_the_things`     | `marginal_minimum` / `marginal_maximum` replaced at runtime — validators and values asserted on run                   |
| Measurement units preserved on created run       | ✅ Asserted  | `test_multi_measurements.py` | `test_multi_measurements` | `with_units()` values (V, A, %) verified on run measurements                                                          |
| Phase with no measurements                       | ✅ Asserted  | `test_multi_measurements.py` | `test_multi_measurements` | Empty measurement list and PASS outcome verified                                                                      |

### 4. Logging

| Scenario              | Status      | File             | Function Name | Details                                          |
| --------------------- | ----------- | ---------------- | ------------- | ------------------------------------------------ |
| INFO log captured     | ✅ Asserted | `test_logger.py` | `test_logger` | `logger.info()` → level=INFO in run logs         |
| ERROR log captured    | ✅ Asserted | `test_logger.py` | `test_logger` | `logger.error()` → level=ERROR in run logs       |
| WARNING log captured  | ✅ Asserted | `test_logger.py` | `test_logger` | `logger.warning()` → level=WARNING in run logs   |
| CRITICAL log captured | ✅ Asserted | `test_logger.py` | `test_logger` | `logger.critical()` → level=CRITICAL in run logs |
| DEBUG log captured    | ✅ Asserted | `test_logger.py` | `test_logger` | `logger.debug()` → level=DEBUG in run logs       |

### 5. Procedure Metadata

| Scenario                                      | Status      | File                        | Function Name                                | Details                                                      |
| --------------------------------------------- | ----------- | --------------------------- | -------------------------------------------- | ------------------------------------------------------------ |
| Procedure version passed through to TofuPilot | ✅ Asserted | `test_procedure_version.py` | `test_procedure_version` | Deterministic `check_button` phase, asserts version `1.2.20` |

### 6. Serial Number Regex

| Scenario                                                     | Status      | File                          | Function Name                              | Details                                                                  |
| ------------------------------------------------------------ | ----------- | ----------------------------- | ------------------------------------------ | ------------------------------------------------------------------------ |
| Missing part number without regex config returns clear error | ✅ Asserted | `test_regex_serial_number.py` | `test_no_part_number_without_regex_config` | No `part_number`, no org regex → server rejects with "part number" error |

### 7. Attachments

| Scenario                           | Status       | File                     | Function Name                                | Details                                                           |
| ---------------------------------- | ------------ | ------------------------ | -------------------------------------------- | ----------------------------------------------------------------- |
| File attachment (image)            | ✅ Asserted  | `test_all_the_things.py` | `test_all_the_things`                        | `attach_from_file("oscilloscope.jpeg")` — name asserted on run    |
| Binary data attachment             | ✅ Asserted  | `test_all_the_things.py` | `test_all_the_things`                        | `attach("name", data.encode("utf-8"))` — name asserted on run     |
| Multiple file types (text + image) | 🔄 Exercised | `test_from_openhtf.py`   | `test_openhtf_run_creation_with_attachments` | `.txt` + `.jpeg` attached in same run; no run property assertions |

### 8. OpenHTF-Specific Features

| Scenario                                      | Status       | File                       | Function Name                            | Details                                                                                                                   |
| --------------------------------------------- | ------------ | -------------------------- | ---------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| Skipped phase included in test definition     | 🔄 Exercised | `test_all_the_things.py`   | `test_all_the_things`                    | `@htf.PhaseOptions(run_if=lambda: False)` — phase defined but neither presence nor SKIP outcome asserted on run           |
| Sub-units via OpenHTF `htf.Test()`            | 🔄 Exercised | `test_openhtf_features.py` | `test_sub_units_via_openhtf`             | Sub-unit created via V2 client, linked via `sub_units` metadata — run creation asserted but sub-unit linkage not verified |
| `allow_nan` in OpenHTF JSON serialization     | 🔄 Exercised | `test_openhtf_features.py` | `test_allow_nan_in_openhtf_json`         | NaN measurement uploaded with `allow_nan=True` on `upload` callback; no run property assertions                           |
| PhaseOptions timeout triggers correct outcome | ✅ Asserted  | `test_openhtf_features.py` | `test_phase_timeout_outcome`             | `@htf.PhaseOptions(timeout_s=1)` → asserts timed-out phase outcome is not PASS                                            |
| Phase with PhaseResult.STOP halts execution   | ✅ Asserted  | `test_openhtf_features.py` | `test_phase_result_stop_halts_execution` | `PhaseResult.STOP` → asserts subsequent phase not present in run phases                                                   |

### 9. Direct Client API — `create_run()` (POST /v1/runs)

> 62k calls/year in prod.

#### 9a. Core Run Creation

| Scenario                              | Status      | File                 | Function Name                            | Details                                                                                                     |
| ------------------------------------- | ----------- | -------------------- | ---------------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| Minimal PASS run                      | ✅ Asserted | `test_create_run.py` | `test_minimal_pass_run`                  | `create_run({"serial_number": "SN"}, run_passed=True)` → response has `id`, V2 lookup confirms outcome=PASS |
| Minimal FAIL run                      | ✅ Asserted | `test_create_run.py` | `test_minimal_fail_run`                  | `run_passed=False` → outcome stored as FAIL on created run                                                  |
| All UnitUnderTest fields roundtrip    | ✅ Asserted | `test_create_run.py` | `test_all_unit_fields_roundtrip`         | serial_number, part_number, revision, batch_number verified on created run (`part_name` deprecated by API)  |
| `started_at` and `duration` preserved | ✅ Asserted | `test_create_run.py` | `test_started_at_and_duration_preserved` | Datetime and timedelta roundtrip — created run timestamps match input values                                |

#### 9b. Procedure Resolution

| Scenario                               | Status      | File                           | Function Name                     | Details                                                                               |
| -------------------------------------- | ----------- | ------------------------------ | --------------------------------- | ------------------------------------------------------------------------------------- |
| Procedure resolved by `procedure_name` | ✅ Asserted | `test_create_run_procedure.py` | `test_procedure_resolved_by_name` | `procedure_name` alongside `procedure_id` → run created (API requires `procedure_id`) |
| Procedure resolved by `procedure_id`   | ✅ Asserted | `test_create_run_procedure.py` | `test_procedure_resolved_by_id`   | Existing procedure matched by ID; run linked correctly                                |
| `procedure_version` stored on run      | ✅ Asserted | `test_create_run_procedure.py` | `test_procedure_version_stored`   | Version tag verified on created run via V2 lookup                                     |

#### 9c. Phases and Measurements

| Scenario                                           | Status       | File                        | Function Name                         | Details                                                                              |
| -------------------------------------------------- | ------------ | --------------------------- | ------------------------------------- | ------------------------------------------------------------------------------------ |
| Phases with PASS and FAIL outcomes preserved       | ✅ Asserted  | `test_create_run_phases.py` | `test_phases_with_mixed_outcomes`     | Multiple Phase dicts with mixed outcomes → each phase outcome matches on created run |
| Measurement with limits (lower_limit, upper_limit) | ✅ Asserted  | `test_create_run_phases.py` | `test_measurement_with_limits`        | Limits roundtrip correctly; measured_value and validators verified                   |
| Measurement units preserved                        | ✅ Asserted  | `test_create_run_phases.py` | `test_measurement_units_preserved`    | `units` field on Measurement dict verified on created run (V, A, %)                  |
| Measurement outcomes (PASS, FAIL, UNSET) preserved | ✅ Asserted  | `test_create_run_phases.py` | `test_measurement_outcomes_preserved` | Each MeasurementOutcome enum value stored and retrievable                            |

#### 9d. Attachments (direct file paths)

| Scenario                                         | Status      | File                             | Function Name                        | Details                                                                  |
| ------------------------------------------------ | ----------- | -------------------------------- | ------------------------------------ | ------------------------------------------------------------------------ |
| Single file attachment uploaded and retrievable  | ✅ Asserted | `test_create_run_attachments.py` | `test_single_file_attachment`        | File path in `attachments` list → attachment name appears on created run |
| Multiple file attachments in single run          | ✅ Asserted | `test_create_run_attachments.py` | `test_multiple_file_attachments`     | Several file paths → all attachment names present on created run         |
| Oversized file (>10MB) rejected with clear error | ✅ Asserted | `test_create_run_attachments.py` | `test_oversized_file_rejected`       | `validate_files()` catches size violation → `SystemExit` raised          |
| Too many attachments (>100) rejected             | ✅ Asserted | `test_create_run_attachments.py` | `test_too_many_attachments_rejected` | Exceeding `CLIENT_MAX_ATTACHMENTS` → `SystemExit` raised                 |

#### 9e. Logs (direct)

| Scenario                                     | Status      | File                      | Function Name                        | Details                                                                                |
| -------------------------------------------- | ----------- | ------------------------- | ------------------------------------ | -------------------------------------------------------------------------------------- |
| Log entries with all levels preserved        | ✅ Asserted | `test_create_run_logs.py` | `test_log_levels_preserved`          | Log dicts with DEBUG through CRITICAL → each level and message verified on created run |
| Log timestamps and source metadata preserved | ✅ Asserted | `test_create_run_logs.py` | `test_log_source_metadata_preserved` | `timestamp`, `source_file`, `line_number` roundtrip on created run                     |

#### 9f. Sub-units (direct)

| Scenario                     | Status      | File                           | Function Name                  | Details                                                                                |
| ---------------------------- | ----------- | ------------------------------ | ------------------------------ | -------------------------------------------------------------------------------------- |
| Sub-units linked to main run | ✅ Asserted | `test_create_run_sub_units.py` | `test_sub_units_linked_to_run` | Pre-create sub-unit via V2, then `sub_units=[{...}]` → linkage verified on created run |

### 10. Direct Client API — `get_runs()` (GET /v1/runs)

> 8k calls/year in prod.

| Scenario                                     | Status      | File               | Function Name                          | Details                                                                                     |
| -------------------------------------------- | ----------- | ------------------ | -------------------------------------- | ------------------------------------------------------------------------------------------- |
| Returns runs for known serial number         | ✅ Asserted | `test_get_runs.py` | `test_returns_run_for_known_serial`    | Create a run, then `get_runs(serial)` → result contains the run ID                         |
| Response structure matches `GetRunsResponse` | ✅ Asserted | `test_get_runs.py` | `test_response_structure`              | `success`, `result` list with run objects containing id, outcome, unit with serial_number   |
| Multiple runs for same serial number         | ✅ Asserted | `test_get_runs.py` | `test_multiple_runs_for_same_serial`   | Create two runs for same serial → `get_runs()` returns both IDs                            |
| Nonexistent serial number → empty result     | ✅ Asserted | `test_get_runs.py` | `test_nonexistent_serial_returns_empty`| `get_runs("GHOST-...")` → success with empty result list, no error                          |
| Empty serial_number → client-side error      | ✅ Asserted | `test_get_runs.py` | `test_empty_serial_returns_client_error`| `get_runs("")` → `success=False` with "serial_number" in error message                    |

### 11. Error Handling

| Scenario                                   | Status      | File              | Function Name                  | Details                                                                          |
| ------------------------------------------ | ----------- | ----------------- | ------------------------------ | -------------------------------------------------------------------------------- |
| Invalid API key → authentication error     | ✅ Asserted | `test_errors.py`  | `test_invalid_api_key`         | `api_key="invalid-key-000"` → `success=False`, status 401/403                    |
| Missing `serial_number` in unit_under_test | ✅ Asserted | `test_errors.py`  | `test_missing_serial_number`   | Required field omitted → `success=False`, status 400                             |
| Network timeout                            | ✅ Asserted | `test_errors.py`  | `test_network_timeout`         | Unreachable server → `success=False` with error dict                             |
| Invalid file path in attachments           | ✅ Asserted | `test_errors.py`  | `test_invalid_file_path`       | Nonexistent file path → `FileNotFoundError` raised by `validate_files()`         |

---

## V1 Summary

> **Scenarios vs pytest items:** Each row counts one unique test scenario (multiple rows can map to the same function). V1 has 43 unique test functions → **87 pytest items**: `test_all_the_things` ×4 (×2 auth × ×2 stream), `test_invalid_api_key` ×1, 41 other functions ×2 (auth).

| Category                       | Scenarios | Asserted | Exercised | Untested |
| ------------------------------ | --------- | -------- | --------- | -------- |
| End-to-End Workflows           | 8         | 7        | 1         | 0        |
| Run Creation from OpenHTF      | 5         | 1        | 4         | 0        |
| Measurements                   | 7         | 6        | 1         | 0        |
| Logging                        | 5         | 5        | 0         | 0        |
| Procedure Metadata             | 1         | 1        | 0         | 0        |
| Serial Number Regex            | 1         | 1        | 0         | 0        |
| Attachments                    | 3         | 2        | 1         | 0        |
| OpenHTF-Specific Features      | 5         | 2        | 3         | 0        |
| Direct Client — `create_run()` | 18        | 18       | 0         | 0        |
| Direct Client — `get_runs()`   | 5         | 5        | 0         | 0        |
| Error Handling                 | 4         | 4        | 0         | 0        |
| **Total**                      | **62**    | **52**   | **10**    | **0**    |

- **Asserted**: Scenario runs and outcome is explicitly asserted on the created run
- **Exercised**: Scenario runs but outcome is not asserted (smoke test / no-crash check)
- **Untested**: No test covers this scenario

**V1 Coverage: 52/62 asserted, 10/62 exercised, 0/62 untested**
**Pytest items: 87** (43 functions: 1×4 + 1×1 + 41×2)
