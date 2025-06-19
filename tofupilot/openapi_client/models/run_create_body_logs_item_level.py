from typing import Literal, cast

RunCreateBodyLogsItemLevel = Literal["CRITICAL", "DEBUG", "ERROR", "INFO", "WARNING"]

RUN_CREATE_BODY_LOGS_ITEM_LEVEL_VALUES: set[RunCreateBodyLogsItemLevel] = {
    "CRITICAL",
    "DEBUG",
    "ERROR",
    "INFO",
    "WARNING",
}


def check_run_create_body_logs_item_level(value: str) -> RunCreateBodyLogsItemLevel:
    if value in RUN_CREATE_BODY_LOGS_ITEM_LEVEL_VALUES:
        return cast(RunCreateBodyLogsItemLevel, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {RUN_CREATE_BODY_LOGS_ITEM_LEVEL_VALUES!r}")
