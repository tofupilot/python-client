from enum import Enum


class RunGetSort(str, Enum):
    CREATEDAT = "createdAt"
    DURATION = "duration"
    STARTEDAT = "startedAt"
    VALUE_0 = "-startedAt"
    VALUE_2 = "-createdAt"
    VALUE_4 = "-duration"

    def __str__(self) -> str:
        return str(self.value)
