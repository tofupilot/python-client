from typing import Optional, Union, TypedDict, List, Literal, Dict
from datetime import datetime, timedelta
from enum import Enum

RunOutcome = Literal["RUNNING", "PASS", "FAIL", "ERROR", "TIMEOUT", "ABORTED"]
LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
Json = Union[Dict[str, object], List]

class StepRequired(TypedDict):
    name: str
    started_at: datetime
    duration: timedelta
    step_passed: bool

class Step(StepRequired, total=False):
    measurement_unit: Optional[str]
    measurement_value: Optional[Union[float, str]]
    limit_low: float
    limit_high: float


class MeasurementOutcome(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    UNSET = "UNSET"


class MeasurementRequired(TypedDict):
    name: str
    outcome: MeasurementOutcome

class Measurement(MeasurementRequired, total=False):
    measured_value: Union[float, str, bool, List[List[float]], Json]
    units: Union[str, List[str]]
    lower_limit: float
    upper_limit: float
    validators: Optional[List[str]]
    docstring: Optional[str]


class PhaseOutcome(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    SKIP = "SKIP"
    ERROR = "ERROR"


class PhaseRequired(TypedDict):
    name: str
    outcome: PhaseOutcome

class Phase(PhaseRequired, total=False):
    measurements: Optional[List[Measurement]]
    docstring: Optional[str]
    
    # These are effectively required:
    start_time: datetime
    end_time: datetime
    # These are deprecated, and should be replaced by they're non _millis equivalent
    start_time_millis: int # TODO: technically only these are allowed and required (should be the opposite)
    end_time_millis: int # TODO: technically only these are allowed and required (should be the opposite)
    # At least one set is required


class Log(TypedDict):
    level: LogLevel
    timestamp: str
    message: str
    source_file: str
    line_number: int


class SubUnit(TypedDict):
    serial_number: str


class UnitUnderTestRequired(TypedDict):
    serial_number: str

class UnitUnderTest(UnitUnderTestRequired, total=False):
    part_number: str
    part_name: Optional[str]
    revision: str
    batch_number: str
