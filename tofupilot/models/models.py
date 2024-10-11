from typing import Optional, Union, TypedDict
from datetime import datetime, timedelta


class Step(TypedDict):
    name: str
    started_at: datetime
    duration: timedelta
    step_passed: bool
    measurement_unit: Optional[str]
    measurement_value: Optional[Union[float, str]]
    limit_low: Optional[float]
    limit_high: Optional[float]


class SubUnit(TypedDict):
    serial_number: str


class UnitUnderTest(TypedDict):
    serial_number: str
    part_number: Optional[str]
    revision: Optional[str]
    batch_number: Optional[str]
