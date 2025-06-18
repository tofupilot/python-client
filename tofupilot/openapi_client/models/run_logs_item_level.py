from typing import Literal, cast

RunLogsItemLevel = Literal["CRITICAL", "DEBUG", "ERROR", "INFO", "WARNING"]

RUN_LOGS_ITEM_LEVEL_VALUES: set[RunLogsItemLevel] = {
    "CRITICAL",
    "DEBUG",
    "ERROR",
    "INFO",
    "WARNING",
}


def check_run_logs_item_level(value: str) -> RunLogsItemLevel:
    if value in RUN_LOGS_ITEM_LEVEL_VALUES:
        return cast(RunLogsItemLevel, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {RUN_LOGS_ITEM_LEVEL_VALUES!r}")
