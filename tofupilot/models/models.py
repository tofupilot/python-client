from typing import Optional, Union, TypedDict, List
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


class Measurement(TypedDict):
    name: str
    outcome: str  # "PASS", "FAIL", "UNSET"
    measured_value: Optional[Union[float, str]]
    units: Optional[str]
    lower_limit: Optional[float]
    upper_limit: Optional[float]
    validators: Optional[List[str]]
    docstring: Optional[str]


class Phase(TypedDict):
    name: str
    outcome: str  # "PASS", "FAIL", "SKIP", "ERROR"
    start_time_millis: int
    end_time_millis: int
    measurements: Optional[List[Measurement]]
    docstring: Optional[str]


class SubUnit(TypedDict):
    serial_number: str


class UnitUnderTest(TypedDict):
    serial_number: str
    part_number: Optional[str]
    part_name: Optional[str]
    revision: Optional[str]
    batch_number: Optional[str]
