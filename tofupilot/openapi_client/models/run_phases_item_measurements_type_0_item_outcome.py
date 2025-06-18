from typing import Literal, cast

RunPhasesItemMeasurementsType0ItemOutcome = Literal["FAIL", "PASS", "UNSET"]

RUN_PHASES_ITEM_MEASUREMENTS_TYPE_0_ITEM_OUTCOME_VALUES: set[RunPhasesItemMeasurementsType0ItemOutcome] = {
    "FAIL",
    "PASS",
    "UNSET",
}


def check_run_phases_item_measurements_type_0_item_outcome(value: str) -> RunPhasesItemMeasurementsType0ItemOutcome:
    if value in RUN_PHASES_ITEM_MEASUREMENTS_TYPE_0_ITEM_OUTCOME_VALUES:
        return cast(RunPhasesItemMeasurementsType0ItemOutcome, value)
    raise TypeError(
        f"Unexpected value {value!r}. Expected one of {RUN_PHASES_ITEM_MEASUREMENTS_TYPE_0_ITEM_OUTCOME_VALUES!r}"
    )
