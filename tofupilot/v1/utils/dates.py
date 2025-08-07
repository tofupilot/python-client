from datetime import timedelta, datetime, timezone
from typing import Optional
import posthog

def timedelta_to_iso(td: timedelta) -> str:
    if td == timedelta():  # Check if timedelta is zero
        return "PT0S"  # Return "PT0S" for zero duration

    days = td.days
    seconds = td.seconds
    microseconds = td.microseconds

    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    iso_duration = "P"
    if days > 0:
        iso_duration += f"{days}D"

    if hours > 0 or minutes > 0 or seconds > 0 or microseconds > 0:
        iso_duration += "T"
        if hours > 0:
            iso_duration += f"{hours}H"
        if minutes > 0:
            iso_duration += f"{minutes}M"
        if seconds > 0 or microseconds > 0:
            iso_duration += f"{seconds}"
            if microseconds > 0:
                iso_duration += f".{microseconds:06d}"
            iso_duration += "S"

    return iso_duration


def duration_to_iso(duration_seconds):
    td = timedelta(seconds=duration_seconds)
    return timedelta_to_iso(td)


def datetime_to_iso(dt: datetime):
    if isinstance(dt, str):
        exception = TypeError(
            f"Expected datetime object, got string: '{dt}'. "
            f"Convert to datetime first: datetime.fromisoformat('{dt}'.replace('Z', '+00:00'))"
        )
        posthog.capture_exception(exception)
        raise exception
    # Ensure the datetime object is timezone-aware and in UTC
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    # Format the datetime and replace '+00:00' with 'Z'
    iso_str = dt.isoformat()
    if iso_str.endswith("+00:00"):
        iso_str = iso_str[:-6] + "Z"
    return iso_str

def datetime_to_iso_optional(dt: Optional[datetime]) -> Optional[str]:
    return datetime_to_iso(dt) if dt is not None else None

def iso_to_datetime(s: str) -> datetime:
    return datetime.fromisoformat(s)

def iso_to_datetime_optional(s: Optional[str]) -> Optional[datetime]:
    return iso_to_datetime(s) if s is not None else None
