from dataclasses import dataclass


@dataclass(frozen=True)
class Policy:
    admin_id: int
    bot_username: str
    archive_timezone: str = "Europe/Minsk"
    max_file_bytes: int = 10 * 1024**3
    part_bytes: int = 8 * 1024**2
    max_open_uploads: int = 10
    upload_idle_seconds: int = 7 * 86400
    session_idle_seconds: int = 30 * 86400
    session_max_seconds: int = 90 * 86400
    trash_retention_seconds: int = 30 * 86400
