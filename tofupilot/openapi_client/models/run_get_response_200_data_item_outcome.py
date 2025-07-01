from enum import Enum


class RunGetResponse200DataItemOutcome(str, Enum):
    ABORTED = "ABORTED"
    ERROR = "ERROR"
    FAIL = "FAIL"
    PASS = "PASS"
    RUNNING = "RUNNING"
    TIMEOUT = "TIMEOUT"

    def __str__(self) -> str:
        return str(self.value)
