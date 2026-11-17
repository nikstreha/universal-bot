from pathlib import Path

from pydantic import BaseModel, ConfigDict


class PersistenceConfiguration(BaseModel):
    model_config = ConfigDict(frozen=True)
    database_path: Path = Path("var/storage.sqlite3")

    @property
    def dsn(self) -> str:
        return "sqlite+aiosqlite:///" + str(self.database_path.resolve())
