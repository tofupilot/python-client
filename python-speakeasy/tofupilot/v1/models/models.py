from typing import Optional, Union, TypedDict, List, Literal
from datetime import datetime, timedelta
from enum import Enum

RunOutcome = Literal["RUNNING", "PASS", "FAIL", "ERROR", "TIMEOUT", "ABORTED"]

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
    measured_value: Union[float, str]
    units: str
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
    start_time_millis: int
    end_time_millis: int

class Phase(PhaseRequired, total=False):
    measurements: Optional[List[Measurement]]
    docstring: Optional[str]

class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


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
