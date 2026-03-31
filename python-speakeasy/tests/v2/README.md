## V2 API Test Scenarios

### 1. Batches

| Scenario                      | Status    | Function Name                                     | Details                                         |
| ----------------------------- | --------- | ------------------------------------------------- | ----------------------------------------------- |
| Empty batch number → error    | ✅ Tested | `test_empty_batch_number_fails`                   | Empty string raises validation error            |
| Batch number too long → error | ✅ Tested | `test_batch_number_too_long_fails`                | Exceeding 100 chars raises error                |
| Special characters → accepted | ✅ Tested | `test_batch_number_with_special_characters`       | Dash, underscore, alphanumeric, mixed           |
| Invalid characters → error    | ✅ Tested | `test_batch_number_with_invalid_characters_fails` | Slash, backslash, space, parens, brackets, etc. |

### 2. Parts

| Scenario                            | Status    | Function Name                           | Details                                            |
| ----------------------------------- | --------- | --------------------------------------- | -------------------------------------------------- |
| **Create**                          |           |                                         |                                                    |
| Empty part number → error           | ✅ Tested | `test_empty_part_number_fails`          | Empty string raises API error                      |
| Part number too long → error        | ✅ Tested | `test_part_number_too_long_fails`       | Exceeding 60 chars raises error                    |
| Part name too long → error          | ✅ Tested | `test_part_name_too_long_fails`         | Exceeding 255 chars raises error                   |
| Revision number too long → error    | ✅ Tested | `test_revision_number_too_long_fails`   | Exceeding 60 chars raises error                    |
| Duplicate part number → CONFLICT    | ✅ Tested | `test_duplicate_part_number_fails`      | Identical number raises ErrorCONFLICT              |
| Case-insensitive uniqueness         | ✅ Tested | `test_part_number_case_insensitive`     | Uppercase variant of existing raises ErrorCONFLICT |
| Special characters in number        | ✅ Tested | `test_part_number_special_characters`   | Hyphen, underscore, dot, slash, unicode, emoji     |
| **Get**                             |           |                                         |                                                    |
| Get existing part                   | ✅ Tested | `test_get_existing_part`                | Returns id, number, name, created_at, revisions    |
| Get part with revisions             | ✅ Tested | `test_get_part_with_revisions`          | Revision id, number, created_at present            |
| Get nonexistent part → NOT_FOUND    | ✅ Tested | `test_get_nonexistent_part`             | Raises ErrorNOTFOUND                               |
| Get part creator info               | ✅ Tested | `test_get_part_created_by_user`         | created_by_user or created_by_station populated    |
| **Update**                          |           |                                         |                                                    |
| Update nonexistent part → NOT_FOUND | ✅ Tested | `test_update_nonexistent_part`          | Raises ErrorNOTFOUND or 403 for stations           |
| Update invalid number format        | ✅ Tested | `test_update_invalid_number_format`     | ErrorNotFound (user, station)                      |
| Update duplicate number → CONFLICT  | ✅ Tested | `test_update_duplicate_part_number`     | Raises ErrorCONFLICT                               |
| Update empty number → error         | ✅ Tested | `test_update_empty_part_number`         | Empty string raises validation error               |
| Update number too long → error      | ✅ Tested | `test_update_part_number_too_long`      | Exceeding 60 chars raises error                    |
| Update name too long → error        | ✅ Tested | `test_update_part_name_too_long`        | Exceeding 255 chars raises error                   |
| Update no fields → error            | ✅ Tested | `test_update_no_fields_provided`        | Requires at least one field                        |
| Update case-insensitive conflict    | ✅ Tested | `test_update_case_insensitive_conflict` | Case-different variant raises ErrorCONFLICT        |
| Update to same number → success     | ✅ Tested | `test_update_to_same_number`            | No-op update with different name succeeds          |

### 3. Procedure Versions

| Scenario                          | Status    | Function Name                               | Details                         |
| --------------------------------- | --------- | ------------------------------------------- | ------------------------------- |
| Empty tag → error                 | ✅ Tested | `test_create_version_empty_name`            | Returns 400, stations get 403   |
| Tag too long → error              | ✅ Tested | `test_create_version_long_name`             | Exceeding 60 chars returns 400  |
| Invalid procedure ID → error      | ✅ Tested | `test_create_version_invalid_procedure_id`  | Invalid UUID returns 400 or 404 |
| Nonexistent procedure → NOT_FOUND | ✅ Tested | `test_create_version_nonexistent_procedure` | APIError (station)              |

### 4. Procedures

| Scenario                       | Status    | Function Name                                        | Details                                       |
| ------------------------------ | --------- | ---------------------------------------------------- | --------------------------------------------- |
| **Create**                     |           |                                                      |                                               |
| Empty name → error             | ✅ Tested | `test_empty_procedure_name_fails`                    | 400 for users, 403 for stations               |
| Whitespace-only name → error   | ✅ Tested | `test_whitespace_only_name_fails`                    | 400 for users, 403 for stations               |
| Leading/trailing spaces        | ✅ Tested | `test_create_procedure_with_leading_trailing_spaces` | Trimmed or rejected                           |
| Very long name → error         | ✅ Tested | `test_very_long_name_handling`                       | 1000+ chars returns 400                       |
| Valid character types          | ✅ Tested | `test_create_procedure_name_character_validation`    | Numbers, underscores, hyphens, periods, mixed |
| **Station Access Control**     |           |                                                      |                                               |
| Station create → 403 FORBIDDEN | ✅ Tested | `test_station_cannot_create_procedure`               | Stations get HTTP 403, users succeed          |
| **Update**                     |           |                                                      |                                               |
| Update name → success          | ✅ Tested | `test_update_procedure_name_success`                 | New name retrievable via list                 |
| Special characters in name     | ✅ Tested | `test_update_procedure_name_with_special_characters` | !@# accepted                                  |
| Unicode in name                | ✅ Tested | `test_update_procedure_name_with_unicode`            | Unicode characters accepted                   |
| Update nonexistent → NOT_FOUND | ✅ Tested | `test_update_non_existent_procedure_fails`           | ErrorNOTFOUND or 403 for stations             |
| Empty name → error             | ✅ Tested | `test_update_procedure_empty_name_fails`             | ErrorBADREQUEST                               |
| Duplicate name → success       | ✅ Tested | `test_update_procedure_duplicate_name_succeeds`      | Names are not unique                          |
| Same name → success            | ✅ Tested | `test_update_procedure_same_name_succeeds`           | No-op update succeeds                         |
| Long name handling             | ✅ Tested | `test_update_procedure_long_name`                    | 200 chars succeeds or validation error        |
| Multiple sequential updates    | ✅ Tested | `test_multiple_updates_same_procedure`               | Final name persists                           |

### 5. Revisions

| Scenario                              | Status    | Function Name                                               | Details                                |
| ------------------------------------- | --------- | ----------------------------------------------------------- | -------------------------------------- |
| **Create**                            |           |                                                             |                                        |
| Empty revision number → error         | ✅ Tested | `test_empty_revision_number_fails`                          | Validation error                       |
| Number too long → error               | ✅ Tested | `test_revision_number_too_long_fails`                       | Exceeding 60 chars raises error        |
| Invalid part number → NOT_FOUND       | ✅ Tested | `test_invalid_part_number_fails`                            | Non-existent part (UUID) raises error  |
| Malformed UUID → NOT_FOUND            | ✅ Tested | `test_malformed_uuid_part_number_fails`                     | Non-UUID string raises error           |
| Duplicate revision → idempotent       | ✅ Tested | `test_duplicate_revision_number_same_part_returns_existing` | Returns existing revision              |
| Same number different parts → success | ✅ Tested | `test_same_revision_number_different_parts_succeeds`        | Distinct revision IDs                  |
| Case-insensitive uniqueness           | ✅ Tested | `test_revision_number_case_insensitive`                     | Uppercase returns same ID as lowercase |
| **Image Upload**                      |           |                                                             |                                        |
| Upload image to revision              | ✅ Tested | `test_update_revision_with_image`                           | APIError (station)                     |
| Upload, verify, and replace image     | ✅ Tested | `test_update_revision_image_and_verify_download`            | APIError (station)                     |
| Remove revision image                 | ✅ Tested | `test_remove_revision_image`                                | APIError (station)                     |
| Update image and number together      | ✅ Tested | `test_update_revision_with_image_and_number`                | APIError (station)                     |

### 6. Runs — Validation

| Scenario                          | Status    | Function Name                                   | Details                                              |
| --------------------------------- | --------- | ----------------------------------------------- | ---------------------------------------------------- |
| Empty serial number → error       | ✅ Tested | `test_create_run_with_empty_serial_number`      | ErrorBADREQUEST with "serial number"                 |
| Whitespace serial number → error  | ✅ Tested | `test_create_run_with_whitespace_serial_number` | ErrorBADREQUEST with "serial number"                 |
| Invalid procedure ID → NOT_FOUND  | ✅ Tested | `test_create_run_with_invalid_procedure_id`     | ErrorNOTFOUND or ErrorFORBIDDEN                      |
| Malformed procedure ID → error    | ✅ Tested | `test_create_run_with_malformed_procedure_id`   | ErrorBADREQUEST with "uuid"                          |
| Invalid outcome → SDK error       | ✅ Tested | `test_create_run_with_invalid_outcome`          | TofuPilotError (user, station)                       |
| End before start → accepted       | ✅ Tested | `test_create_run_with_end_before_start`         | Time order not enforced                              |
| ended_at without outcome → error  | ✅ Tested | `test_create_run_with_ended_at_but_no_outcome`  | TypeError at SDK level                               |
| outcome without ended_at → error  | ✅ Tested | `test_create_run_with_outcome_but_no_ended_at`  | TypeError at SDK level                               |
| Very long serial number → error   | ✅ Tested | `test_create_run_with_very_long_serial_number`  | 1001 chars raises ErrorBADREQUEST                    |
| Invalid batch number → error      | ✅ Tested | `test_create_run_with_invalid_batch_number`     | Empty batch raises ErrorBADREQUEST                   |
| Invalid part number → error       | ✅ Tested | `test_create_run_with_invalid_part_number`      | Empty part raises ErrorBADREQUEST                    |
| Invalid operated_by → error       | ✅ Tested | `test_create_run_with_invalid_operated_by`      | Non-email raises ErrorBADREQUEST                     |
| Missing required fields → error   | ✅ Tested | `test_create_run_without_required_fields`       | Missing serial/procedure/started_at raises TypeError |
| Create run with procedure_version | ✅ Tested | `test_create_run_with_procedure_version`        | Version tag stored and retrievable via get           |
| Create run with docstring         | ✅ Tested | `test_create_run_with_docstring`                | Docstring stored and retrievable via get             |

### 7. Runs — Validators

| Scenario                       | Status    | Function Name                                                 | Details                            |
| ------------------------------ | --------- | ------------------------------------------------------------- | ---------------------------------- |
| **Numeric Operators**          |           |                                                               |                                    |
| `>=` operator                  | ✅ Tested | `test_validator_greater_than_or_equal`                        | Greater than or equal check        |
| `<=` operator                  | ✅ Tested | `test_validator_less_than_or_equal`                           | Less than or equal check           |
| `>` operator                   | ✅ Tested | `test_validator_greater_than`                                 | Strict greater than                |
| `<` operator                   | ✅ Tested | `test_validator_less_than`                                    | Strict less than                   |
| `==` numeric                   | ✅ Tested | `test_validator_equals`                                       | Numeric equality                   |
| `!=` operator                  | ✅ Tested | `test_validator_not_equals`                                   | Not equal check                    |
| **String/Pattern Operators**   |           |                                                               |                                    |
| `==` string                    | ✅ Tested | `test_validator_string_equals`                                | String equality (firmware version) |
| `matches` regex                | ✅ Tested | `test_validator_matches_regex`                                | Regex pattern matching             |
| `in` list                      | ✅ Tested | `test_validator_in_list`                                      | List membership check              |
| `not in` list                  | ✅ Tested | `test_validator_not_in_list`                                  | List exclusion check               |
| `range` operator               | ✅ Tested | `test_validator_range`                                        | [min, max] range check             |
| **Multiple Validators**        |           |                                                               |                                    |
| Multiple on single measurement | ✅ Tested | `test_multiple_validators_on_single_measurement`              | >= and <= forming a range          |
| Mixed pass/fail outcomes       | ✅ Tested | `test_multiple_validators_with_mixed_outcomes`                | One passes, one fails              |
| **Outcomes**                   |           |                                                               |                                    |
| Validator PASS outcome         | ✅ Tested | `test_validator_outcome_pass`                                 | Passing validator                  |
| Validator FAIL outcome         | ✅ Tested | `test_validator_outcome_fail`                                 | Failing validator                  |
| Validator UNSET outcome        | ✅ Tested | `test_validator_outcome_unset`                                | No validation outcome              |
| **Expression**                 |           |                                                               |                                    |
| Expression-only validator      | ✅ Tested | `test_expression_only_validator`                              | No operator/expected_value         |
| Custom expression + operator   | ✅ Tested | `test_validator_with_custom_expression_and_operator`          | Both fields together               |
| **Decisiveness**               |           |                                                               |                                    |
| is_decisive=True               | ✅ Tested | `test_validator_is_decisive_true`                             | Causes measurement failure         |
| is_decisive=False              | ✅ Tested | `test_validator_is_decisive_false`                            | Warning only, no failure           |
| Mixed is_decisive values       | ✅ Tested | `test_validators_mixed_is_decisive`                           | True and False mix                 |
| **Boolean**                    |           |                                                               |                                    |
| Boolean == True                | ✅ Tested | `test_validator_boolean_equals_true`                          | Boolean true check                 |
| Boolean == False               | ✅ Tested | `test_validator_boolean_equals_false`                         | Boolean false check                |
| **Edge Cases**                 |           |                                                               |                                    |
| No validators field            | ✅ Tested | `test_measurement_with_no_validators`                         | Omitted entirely                   |
| Empty validators array         | ✅ Tested | `test_measurement_with_empty_validators_array`                | Empty list                         |
| Null validators                | ✅ Tested | `test_measurement_with_null_validators`                       | Explicitly None                    |
| **Station Access**             |           |                                                               |                                    |
| Station with validators        | ✅ Tested | `test_station_can_create_run_with_validators`                 | Station-only                       |
| Station expression-only        | ✅ Tested | `test_station_can_create_run_with_expression_only_validators` | Station-only                       |
| Station multiple validators    | ✅ Tested | `test_station_can_create_run_with_multiple_validators`        | Station-only                       |
| Station all operator types     | ✅ Tested | `test_station_can_create_run_with_all_validator_types`        | >=, <=, ==, matches, in, range     |
| **Type Mismatch**              |           |                                                               |                                    |
| Numeric op with string value   | ✅ Tested | `test_validator_numeric_operator_with_string_value`           | >= with string accepted            |
| Matches op with numeric value  | ✅ Tested | `test_validator_matches_operator_with_numeric_value`          | matches with number accepted       |
| Boolean on numeric measurement | ✅ Tested | `test_validator_boolean_on_numeric_measurement`               | ==True on numeric                  |
| Numeric on string measurement  | ✅ Tested | `test_validator_numeric_on_string_measurement`                | >=10 on string                     |
| Validator on JSON measurement  | ✅ Tested | `test_validator_on_json_measurement`                          | Validator on dict value            |
| Very large number              | ✅ Tested | `test_validator_with_very_large_number`                       | 9999999999999999                   |
| Negative numbers               | ✅ Tested | `test_validator_with_negative_numbers`                        | Negative range                     |

### 8. Runs — Aggregations

| Scenario                           | Status    | Function Name                                                  | Details                                 |
| ---------------------------------- | --------- | -------------------------------------------------------------- | --------------------------------------- |
| **Basic**                          |           |                                                                |                                         |
| Avg aggregation                    | ✅ Tested | `test_aggregation_avg`                                         | "avg" aggregation type                  |
| Special character types            | ✅ Tested | `test_aggregation_type_with_special_characters`                | %max, max-min, max/range, percentile_95 |
| Multiple aggregations              | ✅ Tested | `test_multiple_aggregations_on_single_measurement`             | min, max, avg, std on one measurement   |
| **Outcomes**                       |           |                                                                |                                         |
| Aggregation PASS                   | ✅ Tested | `test_aggregation_outcome_pass`                                | Passing outcome                         |
| Aggregation FAIL                   | ✅ Tested | `test_aggregation_outcome_fail`                                | Failing outcome                         |
| Aggregation UNSET                  | ✅ Tested | `test_aggregation_outcome_unset`                               | No validation                           |
| **With Validators**                |           |                                                                |                                         |
| Single validator                   | ✅ Tested | `test_aggregation_with_single_validator`                       | >= check on aggregation                 |
| Multiple validators                | ✅ Tested | `test_aggregation_with_multiple_validators`                    | Range check on aggregation              |
| Failing validator                  | ✅ Tested | `test_aggregation_with_failing_validator`                      | is_decisive=True                        |
| is_decisive flag                   | ✅ Tested | `test_aggregation_validator_with_is_decisive`                  | is_decisive=False warning only          |
| Multiple aggs each with validators | ✅ Tested | `test_multiple_aggregations_each_with_validators`              | min, max, avg each validated            |
| **Value Types**                    |           |                                                                |                                         |
| String value                       | ✅ Tested | `test_aggregation_with_string_value`                           | "mode" type with string "OK"            |
| Boolean value                      | ✅ Tested | `test_aggregation_with_boolean_value`                          | "all" type with True                    |
| **Edge Cases**                     |           |                                                                |                                         |
| No aggregations field              | ✅ Tested | `test_measurement_with_no_aggregations`                        | Array value, no aggregations            |
| Empty aggregations array           | ✅ Tested | `test_measurement_with_empty_aggregations_array`               | Empty list                              |
| Null aggregations                  | ✅ Tested | `test_measurement_with_null_aggregations`                      | Explicitly None                         |
| Type mismatch                      | ✅ Tested | `test_aggregation_validator_type_mismatch`                     | String value, numeric validator         |
| Empty array                        | ✅ Tested | `test_aggregation_on_empty_array`                              | Empty measured_value                    |
| Negative values                    | ✅ Tested | `test_aggregation_with_negative_values`                        | Negative measurement values             |
| **Station Access**                 |           |                                                                |                                         |
| Station with aggregations          | ✅ Tested | `test_station_can_create_run_with_aggregations`                | Station-only                            |
| Station with agg + validators      | ✅ Tested | `test_station_can_create_run_with_aggregations_and_validators` | Station-only                            |

### 9. Runs — MDM (Multi-Dimensional Measurements)

| Scenario                        | Status    | Function Name                                     | Details                                           |
| ------------------------------- | --------- | ------------------------------------------------- | ------------------------------------------------- |
| **Basic**                       |           |                                                   |                                                   |
| Basic x_axis/y_axis             | ✅ Tested | `test_mdm_basic_x_axis_y_axis`                    | No validators or aggregations                     |
| Multiple y_axis series          | ✅ Tested | `test_mdm_multiple_y_axis_series`                 | Voltage and current vs same x_axis                |
| **X-Axis Validators**           |           |                                                   |                                                   |
| Single validator                | ✅ Tested | `test_x_axis_with_single_validator`               | >= 0.0                                            |
| Multiple validators             | ✅ Tested | `test_x_axis_with_multiple_validators`            | Range check                                       |
| Fail outcome                    | ✅ Tested | `test_x_axis_validator_with_fail_outcome`         | is_decisive=True                                  |
| **X-Axis Aggregations**         |           |                                                   |                                                   |
| Single aggregation              | ✅ Tested | `test_x_axis_with_single_aggregation`             | "avg"                                             |
| Multiple aggregations           | ✅ Tested | `test_x_axis_with_multiple_aggregations`          | min, max, avg                                     |
| Aggregation with validators     | ✅ Tested | `test_x_axis_aggregation_with_validators`         | Range check on avg                                |
| **Y-Axis Validators**           |           |                                                   |                                                   |
| Single validator                | ✅ Tested | `test_y_axis_with_single_validator`               | >= 2.8                                            |
| Multiple validators             | ✅ Tested | `test_y_axis_with_multiple_validators`            | Range check                                       |
| Multiple series each validated  | ✅ Tested | `test_multiple_y_axis_each_with_validators`       | Per-series validators                             |
| **Y-Axis Aggregations**         |           |                                                   |                                                   |
| Single aggregation              | ✅ Tested | `test_y_axis_with_single_aggregation`             | "avg"                                             |
| Multiple aggregations           | ✅ Tested | `test_y_axis_with_multiple_aggregations`          | min, max, avg, std                                |
| Aggregation with validators     | ✅ Tested | `test_y_axis_aggregation_with_validators`         | <= check on max                                   |
| Multiple series each aggregated | ✅ Tested | `test_multiple_y_axis_each_with_aggregations`     | Per-series aggregations                           |
| **Combined**                    |           |                                                   |                                                   |
| Both axes with validators       | ✅ Tested | `test_both_axes_with_validators`                  | x + y validators simultaneously                   |
| Both axes with aggregations     | ✅ Tested | `test_both_axes_with_aggregations`                | x + y aggregations simultaneously                 |
| Comprehensive all features      | ✅ Tested | `test_comprehensive_I _all_features`              | Axes, validators, aggregations, nested validators |
| **Measurement-Level**           |           |                                                   |                                                   |
| Measurement-level validators    | ✅ Tested | `test_mdm_with_measurement_level_validators`      | Validators outside axes                           |
| Measurement-level aggregations  | ✅ Tested | `test_mdm_with_measurement_level_aggregations`    | Aggregations outside axes                         |
| Measurement + axis validators   | ✅ Tested | `test_mdm_with_measurement_and_axis_validators`   | Both levels simultaneously                        |
| Measurement + axis aggregations | ✅ Tested | `test_mdm_with_measurement_and_axis_aggregations` | Both levels simultaneously                        |
| **Edge Cases**                  |           |                                                   |                                                   |
| Mismatched array lengths        | ✅ Tested | `test_mdm_mismatched_array_lengths`               | x/y different lengths                             |
| Empty arrays                    | ✅ Tested | `test_mdm_empty_arrays`                           | Empty data on both axes                           |
| Negative values both axes       | ✅ Tested | `test_mdm_negative_values_both_axes`              | Negative ranges and validators                    |
| **Station Access**              |           |                                                   |                                                   |
| Station with MDM validators     | ✅ Tested | `test_station_can_create_mdm_with_validators`     | Station-only                                      |
| Station with MDM aggregations   | ✅ Tested | `test_station_can_create_mdm_with_aggregations`   | Station-only                                      |
| Station comprehensive MDM       | ✅ Tested | `test_station_can_create_comprehensive_mdm`       | Station-only                                      |

### 10. Runs — Legacy Limits

| Scenario                        | Status    | Function Name                                    | Details                                 |
| ------------------------------- | --------- | ------------------------------------------------ | --------------------------------------- |
| Lower limit only                | ✅ Tested | `test_legacy_lower_limit_only`                   | No upper_limit                          |
| Upper limit only                | ✅ Tested | `test_legacy_upper_limit_only`                   | No lower_limit                          |
| Both limits                     | ✅ Tested | `test_legacy_both_limits`                        | lower + upper                           |
| Limit failure                   | ✅ Tested | `test_legacy_limits_with_failure`                | Value exceeds upper → FAIL              |
| Coexist with validators         | ✅ Tested | `test_legacy_limits_coexist_with_validators`     | Legacy + new syntax in same run         |
| Multiple measurements           | ✅ Tested | `test_legacy_limits_multiple_measurements`       | Each with own limits                    |
| Negative values                 | ✅ Tested | `test_legacy_limits_with_negative_values`        | Negative boundaries                     |
| Zero boundary                   | ✅ Tested | `test_legacy_limits_with_zero`                   | Zero as limit                           |
| Equal boundaries                | ✅ Tested | `test_legacy_limits_equal_boundaries`            | lower == upper (exact check)            |
| Very small range                | ✅ Tested | `test_legacy_limits_very_small_range`            | Tight tolerance (3.3–3.301)             |
| Integer values                  | ✅ Tested | `test_legacy_limits_integer_values`              | Integer limits                          |
| Float precision                 | ✅ Tested | `test_legacy_limits_float_precision`             | High-precision floats                   |
| Station with legacy limits      | ✅ Tested | `test_station_can_create_run_with_legacy_limits` | Station-only                            |
| Migration legacy → new syntax   | ✅ Tested | `test_migration_from_legacy_to_new_syntax`       | Same name, different syntax across runs |
| Backward compat multiple phases | ✅ Tested | `test_backward_compatibility_multiple_phases`    | Legacy across multiple phases           |

### 11. Runs — Sub-Units Lifecycle

| Scenario                       | Status    | Function Name                         | Details                                            |
| ------------------------------ | --------- | ------------------------------------- | -------------------------------------------------- |
| Sub-units creation and linking | ✅ Tested | `test_sub_units_creation_and_linking` | Full lifecycle: create sub-runs, link via main run |
| Run without sub-units          | ✅ Tested | `test_run_without_sub_units`          | Normal run, correct linkage                        |
| Run with empty sub-units       | ✅ Tested | `test_run_with_empty_sub_units`       | Empty array = no sub-units                         |
| Sub-unit parent change         | ✅ Tested | `test_sub_unit_parent_change`         | Reassignment moves child between parents           |
| Run with single sub-unit       | ✅ Tested | `test_run_with_single_sub_unit`       | One sub-unit reference                             |

### 12. Runs — Search

| Scenario                  | Status    | Function Name                               | Details                                                    |
| ------------------------- | --------- | ------------------------------------------- | ---------------------------------------------------------- |
| Search returns results    | ✅ Tested | `test_search_returns_results_without_error` | Basic, empty, non-existent, special chars, case variations |
| Search with existing data | ✅ Tested | `test_search_with_existing_data`            | Full serial, partial serial, run ID prefix                 |
| Nested fields accessible  | ✅ Tested | `test_nested_fields_accessible`             | procedure.id, procedure.name, unit.serial_number           |

### 13. Stations

| Scenario                       | Status    | Function Name                                   | Details                                                         |
| ------------------------------ | --------- | ----------------------------------------------- | --------------------------------------------------------------- |
| **Get**                        |           |                                                 |                                                                 |
| Get station by ID              | ✅ Tested | `test_get_station_by_id`                        | Name, identifier, procedures, api_key, image, connection_status |
| Get nonexistent → NOT_FOUND    | ✅ Tested | `test_get_station_nonexistent`                  | ErrorNOTFOUND                                                   |
| Get station with procedures    | ✅ Tested | `test_get_station_with_procedures`              | Procedure id, name, identifier, runs_count                      |
| Get connection status          | ✅ Tested | `test_get_station_connection_status`            | None, "connected", or "disconnected"                            |
| Get multiple stations          | ✅ Tested | `test_get_multiple_stations_sequentially`       | Each retrievable by ID                                          |
| **Remove**                     |           |                                                 |                                                                 |
| Remove station without runs    | ✅ Tested | `test_remove_station_without_runs`              | Station unretrievable after removal                             |
| Remove nonexistent → NOT_FOUND | ✅ Tested | `test_remove_station_nonexistent`               | ErrorNOTFOUND, stations get 403                                 |
| Remove multiple stations       | ✅ Tested | `test_remove_multiple_stations`                 | Sequential removal, all unretrievable                           |
| Remove twice → NOT_FOUND       | ✅ Tested | `test_remove_station_twice`                     | Second removal raises ErrorNOTFOUND                             |
| Remove with runs → archives    | ✅ Tested | `test_remove_station_with_runs_archives`        | Station archived, not deleted                                   |
| **Update**                     |           |                                                 |                                                                 |
| Update name                    | ✅ Tested | `test_update_station_name`                      | Identifier unchanged                                            |
| Update identifier              | ✅ Tested | `test_update_station_identifier`                | Name unchanged                                                  |
| Update both fields             | ✅ Tested | `test_update_station_both_fields`               | Name + identifier simultaneously                                |
| Update nonexistent → NOT_FOUND | ✅ Tested | `test_update_station_nonexistent`               | ErrorNOTFOUND                                                   |
| Remove image via update        | ✅ Tested | `test_update_station_remove_image`              | image_id="" → image becomes None                                |
| Partial update                 | ✅ Tested | `test_update_station_partial_update`            | Unspecified fields unchanged                                    |
| Update team (unassign)         | ✅ Tested | `test_update_station_unassign_team`             | `team_id=None` → team becomes None                              |
| **Image Upload**               |           |                                                 |                                                                 |
| Upload image                   | ✅ Tested | `test_update_station_with_image`                | Full init → upload → attach workflow                            |
| Upload, verify, replace        | ✅ Tested | `test_update_station_image_and_verify_download` | Complete image lifecycle                                        |
| Remove image                   | ✅ Tested | `test_remove_station_image`                     | image_id="" → None                                              |
| Image + name update            | ✅ Tested | `test_update_station_with_image_and_name`       | Both in single call                                             |
| Image + identifier update      | ✅ Tested | `test_update_station_with_image_and_identifier` | Both in single call                                             |

### 14. Units

| Scenario                           | Status    | Function Name                                    | Details                                         |
| ---------------------------------- | --------- | ------------------------------------------------ | ----------------------------------------------- |
| **Create**                         |           |                                                  |                                                 |
| Revision not found → NOT_FOUND     | ✅ Tested | `test_create_unit_revision_not_found`            | ErrorNOTFOUND with "revision"                   |
| Duplicate serial → CONFLICT        | ✅ Tested | `test_create_unit_duplicate_serial_number`       | ErrorCONFLICT with "already exists"             |
| Empty serial number → error        | ✅ Tested | `test_create_unit_empty_serial_number`           | Validation error                                |
| Whitespace serial → error          | ✅ Tested | `test_create_unit_whitespace_only_serial_number` | Validation error                                |
| **Children — Add**                 |           |                                                  |                                                 |
| Add single child                   | ✅ Tested | `test_add_single_child`                          | Parent-child relationship verified              |
| Add multiple children sequentially | ✅ Tested | `test_add_multiple_children_sequentially`        | 3 children, all present                         |
| Multi-level hierarchy              | ✅ Tested | `test_create_multi_level_hierarchy`              | Grandparent → parent → child                    |
| Long chain (5 levels)              | ✅ Tested | `test_create_long_parent_child_chain`            | 5-level deep chain                              |
| Add siblings                       | ✅ Tested | `test_add_siblings`                              | 5 siblings under one parent                     |
| **Children — Remove**              |           |                                                  |                                                 |
| Remove single child                | ✅ Tested | `test_remove_single_child`                       | No children/parent after                        |
| Remove one from multiple           | ✅ Tested | `test_remove_one_child_from_multiple`            | 2 of 3 remain                                   |
| Remove all sequentially            | ✅ Tested | `test_remove_all_children_sequentially`          | Count decreases to 0                            |
| Add/remove cycle                   | ✅ Tested | `test_add_remove_cycle`                          | Same child 3 times                              |
| Remove from multi-level            | ✅ Tested | `test_remove_from_multi_level_hierarchy`         | Grandparent loses child, child keeps grandchild |
| Remove by position                 | ✅ Tested | `test_remove_specific_child_by_position`         | Middle, last, first removal                     |
| **Children — Basic Operations**    |           |                                                  |                                                 |
| Complete add/remove cycle          | ✅ Tested | `test_complete_add_remove_cycle`                 | Add, verify, remove, verify independence        |
| Complex sequence                   | ✅ Tested | `test_multiple_operations_sequence`              | Add 3, remove 1, add 1, verify final state      |
| **Children — Cycle Detection**     |           |                                                  |                                                 |
| Self-reference → error             | ✅ Tested | `test_self_reference_prevention`                 | A→A prevented, ErrorBADREQUEST                  |
| 2-level cycle → error              | ✅ Tested | `test_two_level_cycle_prevention`                | A→B, B→A prevented                              |
| 3-level cycle → error              | ✅ Tested | `test_three_level_cycle_prevention`              | A→B→C, C→A prevented                            |
| 4-level cycle → error              | ✅ Tested | `test_four_level_cycle_prevention`               | A→B→C→D, D→A prevented                          |
| Deep cycle (10 levels)             | ✅ Tested | `test_deep_cycle_prevention`                     | Cycles prevented at various depths              |
| Tree structure cycles              | ✅ Tested | `test_multiple_children_no_cycle`                | Valid tree, grandchild→grandparent prevented    |
| **Children — Error Cases**         |           |                                                  |                                                 |
| Add: parent not found              | ✅ Tested | `test_add_child_parent_not_found`                | ErrorNOTFOUND                                   |
| Add: child not found               | ✅ Tested | `test_add_child_child_not_found`                 | ErrorNOTFOUND                                   |
| Add: serial mismatch               | ✅ Tested | `test_add_child_serial_number_mismatch`          | ErrorNOTFOUND                                   |
| Remove: parent not found           | ✅ Tested | `test_remove_child_parent_not_found`             | ErrorNOTFOUND                                   |
| Remove: child not found            | ✅ Tested | `test_remove_child_child_not_found`              | ErrorNOTFOUND                                   |
| Remove: not a child                | ✅ Tested | `test_remove_child_not_actually_child`           | ErrorBADREQUEST with "is not a child of"        |
| Remove: serial mismatch            | ✅ Tested | `test_remove_child_serial_number_mismatch`       | ErrorNOTFOUND                                   |
| Remove: wrong parent               | ✅ Tested | `test_remove_child_from_wrong_parent`            | ErrorBADREQUEST with "is not a child of"        |
| **Children — Validation**          |           |                                                  |                                                 |
| Add: invalid child serial          | ✅ Tested | `test_add_child_invalid_uuid_format`             | Exception raised                                |
| Add: empty child serial            | ✅ Tested | `test_add_child_empty_serial_number`             | Exception raised                                |
| Add: whitespace child serial       | ✅ Tested | `test_add_child_whitespace_serial_number`        | Exception raised                                |
| Remove: invalid child serial       | ✅ Tested | `test_remove_child_invalid_uuid_format`          | Exception raised                                |
| Add: empty parent serial           | ✅ Tested | `test_add_child_empty_parent_serial`             | Exception raised                                |
| Remove: empty parent serial        | ✅ Tested | `test_remove_child_empty_parent_serial`          | Exception raised                                |
| Long serial numbers (60 chars)     | ✅ Tested | `test_very_long_serial_numbers`                  | Max length accepted                             |
| Special chars in serials           | ✅ Tested | `test_special_characters_in_serial_numbers`      | Underscores, dashes accepted                    |
| Serial > 60 chars → rejected       | ✅ Tested | `test_serial_number_over_60_chars`               | Exceeding max length rejected                   |

---

### 15. Runs — Get, Update, Delete

| Scenario                                 | Status    | Function Name                                   | Details                                                   |
| ---------------------------------------- | --------- | ----------------------------------------------- | --------------------------------------------------------- |
| **Get**                                  |           |                                                 |                                                           |
| Get run by ID                            | ✅ Tested | `test_get_run_by_id`                            | Verify id, outcome, timestamps, duration, procedure, unit |
| Get nonexistent run → NOT_FOUND          | ✅ Tested | `test_get_nonexistent_run`                      | `runs.get(id=uuid4())` → ErrorNOTFOUND                    |
| Get run includes phases and measurements | ✅ Tested | `test_get_run_includes_phases_and_measurements` | Verify nested phase/measurement/validator structure       |
| Get run includes logs                    | ✅ Tested | `test_get_run_includes_logs`                    | Verify INFO + WARNING logs with correct messages          |
| Get run includes sub-units               | ✅ Tested | `test_get_run_includes_sub_units`               | Create sub-unit run, link via main run, verify in get     |
| **Update**                               |           |                                                 |                                                           |
| Update run with attachments              | ✅ Tested | `test_update_run_with_attachment`               | Initialize, upload, update, verify via get                |
| Update nonexistent run → NOT_FOUND       | ✅ Tested | `test_update_nonexistent_run`                   | `runs.update(id=uuid4())` → ErrorNOTFOUND                 |
| **Delete**                               |           |                                                 |                                                           |
| Delete single run                        | ✅ Tested | `test_delete_single_run`                        | Create, delete, verify gone via get → ErrorNOTFOUND       |
| Delete multiple runs                     | ✅ Tested | `test_delete_multiple_runs`                     | Create 3, delete all, verify all gone                     |
| Delete nonexistent run → error           | ✅ Tested | `test_delete_nonexistent_run`                   | `runs.delete(ids=[uuid4()])` → ErrorNOTFOUND              |
| Delete run twice → error                 | ✅ Tested | `test_delete_run_twice`                         | Second delete → ErrorNOTFOUND                             |
| Station cannot delete runs → 403         | ✅ Tested | `test_station_cannot_delete_runs`               | `assert_station_access_forbidden` on delete               |

### 16. Runs — List (Filtering & Pagination)

| Scenario                        | Status    | Function Name                              | Details                                                    |
| ------------------------------- | --------- | ------------------------------------------ | ---------------------------------------------------------- |
| List with outcome filter        | ✅ Tested | `test_list_with_outcome_filter`            | PASS + FAIL runs, filter PASS only, verify FAIL excluded   |
| List with procedure_id filter   | ✅ Tested | `test_list_with_procedure_id_filter`       | All results have matching procedure.id                     |
| List with serial_number filter  | ✅ Tested | `test_list_with_serial_number_filter`      | Create with unique serial, filter, verify found            |
| List with part_number filter    | ✅ Tested | `test_list_with_part_number_filter`        | Create with unique part, filter, verify found              |
| List with date range filter     | ✅ Tested | `test_list_with_date_range_filter`         | `started_after` / `started_before` window around known run |
| List with created_by filter     | ✅ Tested | `test_list_with_created_by_user_filter`    | Get user ID from run, filter by `created_by_user_ids`      |
| List with duration range        | ✅ Tested | `test_list_with_duration_range`            | 5-min run, filter PT4M–PT6M, verify found                  |
| List pagination (cursor)        | ✅ Tested | `test_list_pagination`                     | 3 runs, limit=1, verify has_more + cursor yields next page |
| List sort order (asc/desc)      | ✅ Tested | `test_list_sort_order`                     | Asc vs desc on started_at, verify first result differs     |
| List with limit                 | ✅ Tested | `test_list_with_limit`                     | `limit=2` → at most 2 results                              |
| List empty result               | ✅ Tested | `test_list_empty_result`                   | Non-matching serial → empty list, no error                 |
| List with ids filter            | ✅ Tested | `test_list_with_ids_filter`                | Create run, filter by `ids=[id]`, verify exact match       |
| List with procedure_versions    | ✅ Tested | `test_list_with_procedure_versions_filter` | Create run with version tag, filter, verify found          |
| List with revision_numbers      | ✅ Tested | `test_list_with_revision_numbers_filter`   | Create part+revision+run, filter by revision, verify found |
| List with ended_at date range   | ✅ Tested | `test_list_with_ended_at_date_range`       | `ended_after` / `ended_before` window around known run     |
| List with created_at date range | ✅ Tested | `test_list_with_created_at_date_range`     | `created_after` / `created_before` window around new run   |
| List with created_by_station    | ✅ Tested | `test_list_with_created_by_station_filter` | Station-auth run, get station ID, filter, verify found     |
| List with operated_by filter    | ✅ Tested | `test_list_with_operated_by_filter`        | Run with `operated_by`, get operator ID, filter, verify    |

### 17. Procedures — List, Get, Delete

| Scenario                              | Status    | Function Name                             | Details                                                   |
| ------------------------------------- | --------- | ----------------------------------------- | --------------------------------------------------------- |
| **List**                              |           |                                           |                                                           |
| List all procedures                   | ✅ Tested | `test_list_all_procedures`                | Default params, verify response structure and limit       |
| List with search query                | ✅ Tested | `test_list_with_search_query`             | Create with unique name, search, verify found             |
| List pagination (cursor)              | ✅ Tested | `test_list_pagination`                    | limit=1, verify has_more + cursor yields different page   |
| List with date range filter           | ✅ Tested | `test_list_with_date_range_filter`        | `created_after` / `created_before` window around new proc |
| **Get**                               |           |                                           |                                                           |
| Get procedure by ID                   | ✅ Tested | `test_get_procedure_by_id`                | Verify id, name, created_at, runs_count, stations         |
| Get nonexistent procedure → NOT_FOUND | ✅ Tested | `test_get_nonexistent_procedure`          | `procedures.get(id=uuid4())` → ErrorNOTFOUND              |
| Get procedure includes recent_runs    | ✅ Tested | `test_get_procedure_includes_recent_runs` | Verify recent_runs and stations lists in response         |
| **Delete**                            |           |                                           |                                                           |
| Delete procedure                      | ✅ Tested | `test_delete_procedure`                   | Create, delete, verify gone via get → ErrorNOTFOUND       |
| Delete nonexistent procedure → error  | ✅ Tested | `test_delete_nonexistent_procedure`       | `procedures.delete(id=uuid4())` → ErrorNOTFOUND           |
| Station cannot delete procedure → 403 | ✅ Tested | `test_station_cannot_delete_procedure`    | `assert_station_access_forbidden` on delete               |

### 18. Procedure Versions — Get, Delete

| Scenario                            | Status    | Function Name                        | Details                                         |
| ----------------------------------- | --------- | ------------------------------------ | ----------------------------------------------- |
| Get version by tag                  | ✅ Tested | `test_get_version_by_tag`            | `procedures.versions.get(procedure_id, tag)`    |
| Get nonexistent version → NOT_FOUND | ✅ Tested | `test_get_nonexistent_version`       | Invalid tag → ErrorNOTFOUND                     |
| Delete version                      | ✅ Tested | `test_delete_version`                | `procedures.versions.delete(procedure_id, tag)` |
| Delete nonexistent version → error  | ✅ Tested | `test_delete_nonexistent_version`    | Invalid tag → ErrorNOTFOUND                     |
| Station cannot delete version → 403 | ✅ Tested | `test_station_cannot_delete_version` | Station access control on delete                |

### 19. Units — List, Get, Update, Delete

| Scenario                            | Status    | Function Name                              | Details                                                     |
| ----------------------------------- | --------- | ------------------------------------------ | ----------------------------------------------------------- |
| **List**                            |           |                                            |                                                             |
| List all units                      | ✅ Tested | `test_list_all_units`                      | `units.list()` → paginated list                             |
| List with serial_number filter      | ✅ Tested | `test_list_with_serial_number_filter`      | `serial_numbers=[...]` filter                               |
| List with part_number filter        | ✅ Tested | `test_list_with_part_number_filter`        | `part_numbers=[...]` filter                                 |
| List with search query              | ✅ Tested | `test_list_with_search_query`              | `search_query="..."` filter                                 |
| List exclude units with parent      | ✅ Tested | `test_list_exclude_units_with_parent`      | `exclude_units_with_parent=True` filters children           |
| List pagination (cursor)            | ✅ Tested | `test_list_pagination`                     | Multiple pages via cursor token                             |
| List with ids filter                | ✅ Tested | `test_list_with_ids_filter`                | Create unit, filter by `ids=[id]`, verify exact match       |
| List with revision_numbers filter   | ✅ Tested | `test_list_with_revision_numbers_filter`   | Filter by revision number, verify unit found                |
| List with batch_numbers filter      | ✅ Tested | `test_list_with_batch_numbers_filter`      | Create unit via run with batch, filter, verify found        |
| List with date range filter         | ✅ Tested | `test_list_with_created_at_date_range`     | `created_after` / `created_before` window around new unit   |
| List with created_by_user filter    | ✅ Tested | `test_list_with_created_by_user_filter`    | Get creator user ID, filter, verify found (user auth only)  |
| List with created_by_station filter | ✅ Tested | `test_list_with_created_by_station_filter` | Get creator station ID, filter, verify found (station auth) |
| List sort order                     | ✅ Tested | `test_list_sort_order`                     | Asc vs desc on created_at, verify first result differs      |
| **Get**                             |           |                                            |                                                             |
| Get unit by serial number           | ✅ Tested | `test_get_unit_by_serial_number`           | `units.get(serial_number)` → full unit                      |
| Get nonexistent unit → NOT_FOUND    | ✅ Tested | `test_get_nonexistent_unit`                | Invalid serial → ErrorNOTFOUND                              |
| Get unit includes children          | ✅ Tested | `test_get_unit_includes_children`          | Verify children list in response                            |
| Get unit includes parent            | ✅ Tested | `test_get_unit_includes_parent`            | Verify parent reference in response                         |
| Get unit includes runs              | ✅ Tested | `test_get_unit_includes_runs`              | Verify created_during run on unit                           |
| **Update**                          |           |                                            |                                                             |
| Update serial number                | ✅ Tested | `test_update_serial_number`                | `units.update(serial, new_serial_number="...")`             |
| Update part/revision                | ✅ Tested | `test_update_part_revision`                | Move unit to different part/revision                        |
| Update batch assignment             | ✅ Tested | `test_update_batch_assignment`             | `batch_number="..."` reassigns batch                        |
| Update nonexistent unit → NOT_FOUND | ✅ Tested | `test_update_nonexistent_unit`             | Invalid serial → ErrorNOTFOUND                              |
| Update duplicate serial → CONFLICT  | ✅ Tested | `test_update_duplicate_serial`             | New serial already exists → ErrorCONFLICT                   |
| **Delete**                          |           |                                            |                                                             |
| Delete unit by serial number        | ✅ Tested | `test_delete_unit_by_serial_number`        | `units.delete(serial_numbers=[...])`                        |
| Delete nonexistent unit → error     | ✅ Tested | `test_delete_nonexistent_unit`             | Invalid serial → ErrorNOTFOUND                              |
| Delete unit with children           | ✅ Tested | `test_delete_unit_with_children`           | Parent deleted, child becomes orphan                        |

### 20. Stations — Create, List, Get Current

| Scenario                              | Status    | Function Name                                  | Details                                               |
| ------------------------------------- | --------- | ---------------------------------------------- | ----------------------------------------------------- |
| **Create**                            |           |                                                |                                                       |
| Create station                        | ✅ Tested | `test_create_station`                          | `stations.create(name)` → auto-generated identifier   |
| Create station with duplicate name    | ✅ Tested | `test_create_station_with_duplicate_name`      | Names are not unique → should succeed                 |
| Create station empty name → error     | ✅ Tested | `test_create_station_empty_name_fails`         | Validation error                                      |
| **List**                              |           |                                                |                                                       |
| List all stations                     | ✅ Tested | `test_list_all_stations`                       | `stations.list()` → paginated list                    |
| List with search query                | ✅ Tested | `test_list_with_search_query`                  | `search_query="..."` filters by name/identifier       |
| List pagination (cursor)              | ✅ Tested | `test_list_pagination`                         | Multiple pages via cursor token                       |
| **Get Current**                       |           |                                                |                                                       |
| Get current station (station auth)    | ✅ Tested | `test_get_current_station_with_station_auth`   | `stations.get_current()` → authenticated station info |
| Get current station (user auth) → 403 | ✅ Tested | `test_get_current_station_user_auth_forbidden` | Only station API keys can call this                   |

### 21. Batches — List, Get, Update, Delete

| Scenario                             | Status    | Function Name                            | Details                                                    |
| ------------------------------------ | --------- | ---------------------------------------- | ---------------------------------------------------------- |
| **List**                             |           |                                          |                                                            |
| List all batches                     | ✅ Tested | `test_list_all_batches`                  | `batches.list()` → paginated list                          |
| List with number filter              | ✅ Tested | `test_list_with_number_filter`           | `numbers=[...]` filter                                     |
| List with part_number filter         | ✅ Tested | `test_list_with_part_number_filter`      | `part_numbers=[...]` filter                                |
| List with search query               | ✅ Tested | `test_list_with_search_query`            | `search_query="..."` filter                                |
| List pagination (cursor)             | ✅ Tested | `test_list_pagination`                   | Multiple pages via cursor token                            |
| List with ids filter                 | ✅ Tested | `test_list_with_ids_filter`              | Create batch, filter by `ids=[id]`, verify exact match     |
| List with date range filter          | ✅ Tested | `test_list_with_created_at_date_range`   | `created_after` / `created_before` window around new batch |
| List with revision_numbers filter    | ✅ Tested | `test_list_with_revision_numbers_filter` | Create part+revision+run with batch, filter by revision    |
| List sort order                      | ✅ Tested | `test_list_sort_order`                   | Asc vs desc on created_at, verify first result differs     |
| **Get**                              |           |                                          |                                                            |
| Get batch by number                  | ✅ Tested | `test_get_batch_by_number`               | `batches.get(number)` → batch with units                   |
| Get nonexistent batch → NOT_FOUND    | ✅ Tested | `test_get_nonexistent_batch`             | Invalid number → ErrorNOTFOUND                             |
| **Update**                           |           |                                          |                                                            |
| Update batch number                  | ✅ Tested | `test_update_batch_number`               | `batches.update(number, new_number="...")`                 |
| Update nonexistent batch → NOT_FOUND | ✅ Tested | `test_update_nonexistent_batch`          | Invalid number → ErrorNOTFOUND                             |
| Update duplicate number → CONFLICT   | ✅ Tested | `test_update_duplicate_number`           | New number already exists → ErrorCONFLICT                  |
| **Delete**                           |           |                                          |                                                            |
| Delete batch                         | ✅ Tested | `test_delete_batch`                      | `batches.delete(number)` → units disassociated             |
| Delete nonexistent batch → error     | ✅ Tested | `test_delete_nonexistent_batch`          | Invalid number → ErrorNOTFOUND                             |

### 22. Parts — List, Delete

| Scenario                        | Status    | Function Name                  | Details                                              |
| ------------------------------- | --------- | ------------------------------ | ---------------------------------------------------- |
| **List**                        |           |                                |                                                      |
| List all parts                  | ✅ Tested | `test_list_all_parts`          | `parts.list(limit=5)` → paginated list               |
| List with search query          | ✅ Tested | `test_list_with_search_query`  | Create part, search by number, verify found          |
| List pagination (cursor)        | ✅ Tested | `test_list_pagination`         | limit=1, verify has_more + cursor yields next page   |
| List sort order                 | ✅ Tested | `test_list_sort_order`         | asc vs desc on created_at, verify different ordering |
| **Delete**                      |           |                                |                                                      |
| Delete part                     | ✅ Tested | `test_delete_part`             | Create, delete, verify gone + cascade deletes revs   |
| Delete nonexistent part → error | ✅ Tested | `test_delete_nonexistent_part` | Invalid number → ErrorNOTFOUND                       |

### 23. Revisions — Get, Delete

| Scenario                             | Status    | Function Name                          | Details                                             |
| ------------------------------------ | --------- | -------------------------------------- | --------------------------------------------------- |
| **Get**                              |           |                                        |                                                     |
| Get revision by part + number        | ✅ Tested | `test_get_revision_by_part_and_number` | Verify id, number, created_at, part, units          |
| Get nonexistent revision → NOT_FOUND | ✅ Tested | `test_get_nonexistent_revision`        | Valid part, invalid revision → ErrorNOTFOUND        |
| **Delete**                           |           |                                        |                                                     |
| Delete revision                      | ✅ Tested | `test_delete_revision`                 | Create, delete, verify gone via get → ErrorNOTFOUND |
| Delete nonexistent revision → error  | ✅ Tested | `test_delete_nonexistent_revision`     | Valid part, invalid revision → ErrorNOTFOUND        |
| Station cannot delete revision → 403 | ✅ Tested | `test_station_cannot_delete_revision`  | `assert_station_access_forbidden` on delete         |

### 24. User

| Scenario         | Status    | Function Name           | Details                                                 |
| ---------------- | --------- | ----------------------- | ------------------------------------------------------- |
| List users       | ✅ Tested | `test_list_all_users`   | `user.list()` → all org users (user + station auth)              |
| Get current user | ✅ Tested | `test_get_current_user` | `user.list(current=True)` → self only; stations get empty list   |

### 25. Attachments

| Scenario                           | Status    | Function Name                         | Details                                             |
| ---------------------------------- | --------- | ------------------------------------- | --------------------------------------------------- |
| Initialize upload (happy path)     | ✅ Tested |                                       | Used in 12 tests across runs/stations/revisions     |
| Initialize with empty name → error | ✅ Tested | `test_initialize_with_empty_name`     | `attachments.initialize(name="")` → ErrorBADREQUEST |
| Initialize with very long name     | ✅ Tested | `test_initialize_with_very_long_name` | 1001-char name → ErrorBADREQUEST                    |

---

## Summary

> **Scenarios vs pytest items:** Each row below counts one unique test function. V2 has 346 unique test functions → **715 pytest items**: 344 functions ×2 (user + station auth), 1 function ×26 (`test_batch_number_with_invalid_characters_fails`: 13 invalid char params × 2 auth), 1 function ×1 (`test_special_characters_in_serial_numbers`: user_client only).

| Category                   | Scenarios | Passed  | Untested |
| -------------------------- | --------- | ------- | -------- |
| Batches                    | 20        | 20      | 0        |
| Parts                      | 26        | 26      | 0        |
| Procedure Versions         | 9         | 9       | 0        |
| Procedures                 | 25        | 25      | 0        |
| Revisions                  | 16        | 16      | 0        |
| Runs — Validation          | 15        | 15      | 0        |
| Runs — Validators          | 37        | 37      | 0        |
| Runs — Aggregations        | 21        | 21      | 0        |
| Runs — MDM                 | 28        | 28      | 0        |
| Runs — Legacy Limits       | 15        | 15      | 0        |
| Runs — Sub-Units Lifecycle | 5         | 5       | 0        |
| Runs — Search              | 3         | 3       | 0        |
| Runs — List                | 18        | 18      | 0        |
| Runs — Get/Update/Delete   | 12        | 12      | 0        |
| Stations                   | 30        | 30      | 0        |
| Units                      | 66        | 66      | 0        |
| User                       | 2         | 2       | 0        |
| Attachments                | 3         | 3       | 0        |
| **Total**                  | **351**   | **351** | **0**    |

**V2 Coverage: 351/351 scenarios passing, 0 untested (100% method-param coverage)**
**Pytest items: 715** (346 functions: 344×2 + 1×26 + 1×1)
