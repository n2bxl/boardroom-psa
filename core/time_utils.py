from __future__ import annotations

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from tzlocal import get_localzone_name

def utc_now_iso() -> str:
    """
    Store UTC in ISO format.
    Example: 2026-03-06T04:15:00+00:00
    """
    return datetime.now(timezone.utc).isoformat()

def resolve_timezone(session_state, defaults) -> str:
    """
    Priority:
    1) manual override
    2) host system timezone
    3) UTC
    """
    override = session_state.get(
        "timezone_override",
        defaults.get("timezone_override", "")
    )
    use_system = session_state.get(
        "use_system_timezone",
        defaults.get("use_system_timezone", True)
    )

    if override:
        return override
    
    if use_system:
        try:
            return get_localzone_name()
        except Exception:
            pass

    return "UTC"

def format_timestamp_for_display(ts: str | None, tz_name: str) -> str:
    if not ts:
        return ""

    try:
        dt = datetime.fromisoformat(ts)
        local_dt = dt.astimezone(ZoneInfo(tz_name))
        return local_dt.strftime("%Y-%m-%d %I:%M %p")
    except Exception:
        return ts