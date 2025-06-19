from typing import Literal, cast

RunCreateBodyPhasesItemMeasurementsType0ItemOutcome = Literal["FAIL", "PASS", "UNSET"]

RUN_CREATE_BODY_PHASES_ITEM_MEASUREMENTS_TYPE_0_ITEM_OUTCOME_VALUES: set[
    RunCreateBodyPhasesItemMeasurementsType0ItemOutcome
] = {
    "FAIL",
    "PASS",
    "UNSET",
}


def check_run_create_body_phases_item_measurements_type_0_item_outcome(
    value: str,
) -> RunCreateBodyPhasesItemMeasurementsType0ItemOutcome:
    if value in RUN_CREATE_BODY_PHASES_ITEM_MEASUREMENTS_TYPE_0_ITEM_OUTCOME_VALUES:
        return cast(RunCreateBodyPhasesItemMeasurementsType0ItemOutcome, value)
    raise TypeError(
        f"Unexpected value {value!r}. Expected one of {RUN_CREATE_BODY_PHASES_ITEM_MEASUREMENTS_TYPE_0_ITEM_OUTCOME_VALUES!r}"
    )
