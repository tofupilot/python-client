from typing import Optional, TypedDict
from datetime import datetime, timedelta


class Step(TypedDict):
    name: str
    started_at: datetime
    duration: timedelta
    passed: bool
    unit: Optional[str]
    measured_value: Optional[float]
    min_threshold: Optional[float]
    max_threshold: Optional[float]
