from typing import Optional, TypedDict
from datetime import datetime, timedelta


class Step(TypedDict):
    name: str
    started_at: datetime
    duration: timedelta
    step_passed: bool
    measurement_unit: Optional[str]
    measurement_value: Optional[float]
    limit_low: Optional[float]
    limit_high: Optional[float]
