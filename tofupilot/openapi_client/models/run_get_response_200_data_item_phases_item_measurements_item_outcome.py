from enum import Enum


class RunGetResponse200DataItemPhasesItemMeasurementsItemOutcome(str, Enum):
    FAIL = "FAIL"
    PASS = "PASS"
    UNSET = "UNSET"

    def __str__(self) -> str:
        return str(self.value)
