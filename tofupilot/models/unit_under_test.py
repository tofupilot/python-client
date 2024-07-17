from typing import Optional, TypedDict


class UnitUnderTest(TypedDict):
    part_number: str
    serial_number: str
    revision: Optional[str]
