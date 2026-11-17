import time
from datetime import datetime
from zoneinfo import ZoneInfo

from universal_bot.application.port.clock import IClock


class SystemClock(IClock):
    def now(self) -> int:
        return int(time.time())

    def archive_date(self, timezone: str) -> str:
        return datetime.now(ZoneInfo(timezone)).date().isoformat()
