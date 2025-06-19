from typing import Literal, cast

RunCreateBodyPhasesItemOutcome = Literal["ERROR", "FAIL", "PASS", "SKIP"]

RUN_CREATE_BODY_PHASES_ITEM_OUTCOME_VALUES: set[RunCreateBodyPhasesItemOutcome] = {
    "ERROR",
    "FAIL",
    "PASS",
    "SKIP",
}


def check_run_create_body_phases_item_outcome(value: str) -> RunCreateBodyPhasesItemOutcome:
    if value in RUN_CREATE_BODY_PHASES_ITEM_OUTCOME_VALUES:
        return cast(RunCreateBodyPhasesItemOutcome, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {RUN_CREATE_BODY_PHASES_ITEM_OUTCOME_VALUES!r}")
