from typing import Literal, cast

RunCreateBodyOutcome = Literal["ABORTED", "ERROR", "FAIL", "PASS", "RUNNING", "TIMEOUT"]

RUN_CREATE_BODY_OUTCOME_VALUES: set[RunCreateBodyOutcome] = {
    "ABORTED",
    "ERROR",
    "FAIL",
    "PASS",
    "RUNNING",
    "TIMEOUT",
}


def check_run_create_body_outcome(value: str) -> RunCreateBodyOutcome:
    if value in RUN_CREATE_BODY_OUTCOME_VALUES:
        return cast(RunCreateBodyOutcome, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {RUN_CREATE_BODY_OUTCOME_VALUES!r}")
