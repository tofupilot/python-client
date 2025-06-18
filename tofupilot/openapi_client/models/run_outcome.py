from typing import Literal, cast

RunOutcome = Literal["ABORTED", "ERROR", "FAIL", "PASS", "RUNNING", "TIMEOUT"]

RUN_OUTCOME_VALUES: set[RunOutcome] = {
    "ABORTED",
    "ERROR",
    "FAIL",
    "PASS",
    "RUNNING",
    "TIMEOUT",
}


def check_run_outcome(value: str) -> RunOutcome:
    if value in RUN_OUTCOME_VALUES:
        return cast(RunOutcome, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {RUN_OUTCOME_VALUES!r}")
