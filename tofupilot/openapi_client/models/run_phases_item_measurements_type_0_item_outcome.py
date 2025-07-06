from enum import Enum


class RunPhasesItemMeasurementsType0ItemOutcome(str, Enum):
    FAIL = "FAIL"
    PASS = "PASS"
    UNSET = "UNSET"

    def __str__(self) -> str:
        return str(self.value)
