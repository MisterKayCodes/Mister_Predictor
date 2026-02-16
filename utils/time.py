from datetime import datetime, timezone
import pytz


def get_now_utc():
    return datetime.now(timezone.utc)


def format_for_display(dt: datetime, local_tz: str = "Europe/London"):
    target_tz = pytz.timezone(local_tz)
    local_dt = dt.astimezone(target_tz)
    return local_dt.strftime("%d %b, %H:%M")


def is_match_live(start_time_utc: datetime):
    now = get_now_utc()
    diff = (now - start_time_utc).total_seconds() / 60
    return 0 <= diff <= 110
