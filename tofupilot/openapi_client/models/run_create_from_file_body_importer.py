from enum import Enum


class RunCreateFromFileBodyImporter(str, Enum):
    OPENHTF = "OPENHTF"

    def __str__(self) -> str:
        return str(self.value)
