import os
from datetime import datetime, date, time, timedelta
from zoneinfo import ZoneInfo

def app_tz() -> ZoneInfo:
    return ZoneInfo(os.getenv("APP_TZ", "America/Mexico_City"))

def compute_week_bounds(fecha_corte: date) -> tuple[datetime, datetime]:
    local = datetime.combine(fecha_corte, time.min).replace(tzinfo=app_tz())
    monday = local - timedelta(days=local.weekday())  # Monday=0
    week_start = monday.replace(hour=0, minute=0, second=0, microsecond=0)
    week_end = (week_start + timedelta(days=7)) - timedelta(seconds=1)
    return week_start, week_end
