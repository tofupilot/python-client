from datetime import timedelta, datetime


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


def datetime_to_iso(dt: datetime):
    # Note: using dt.isoformat() does not add the trailing 'Z' which prevents the iso string from being recognized by TP' API
    return dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
