from enum import Enum


class RunPhasesItemOutcome(str, Enum):
    ERROR = "ERROR"
    FAIL = "FAIL"
    PASS = "PASS"
    SKIP = "SKIP"

    def __str__(self) -> str:
        return str(self.value)
