from typing import Literal, cast

RunPhasesItemOutcome = Literal["ERROR", "FAIL", "PASS", "SKIP"]

RUN_PHASES_ITEM_OUTCOME_VALUES: set[RunPhasesItemOutcome] = {
    "ERROR",
    "FAIL",
    "PASS",
    "SKIP",
}


def check_run_phases_item_outcome(value: str) -> RunPhasesItemOutcome:
    if value in RUN_PHASES_ITEM_OUTCOME_VALUES:
        return cast(RunPhasesItemOutcome, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {RUN_PHASES_ITEM_OUTCOME_VALUES!r}")
