from datetime import datetime
from zoneinfo import ZoneInfo


def get_current_time(timezone: str) -> str:
    return datetime.now(ZoneInfo(timezone)).isoformat()
