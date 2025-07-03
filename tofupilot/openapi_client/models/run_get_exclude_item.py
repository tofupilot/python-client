from enum import Enum


class RunGetExcludeItem(str, Enum):
    ALL = "all"
    ATTACHMENTS = "attachments"
    CREATEDBY = "createdBy"
    LOGS = "logs"
    MEASUREMENTS = "measurements"
    PHASES = "phases"
    PROCEDURE = "procedure"
    PROCEDUREVERSION = "procedureVersion"
    UNIT = "unit"

    def __str__(self) -> str:
        return str(self.value)
