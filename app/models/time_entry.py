from datetime import datetime

from beanie import Document
from pydantic import Field


class TimeEntry(Document):
    user_id: str
    project_id: str
    start: datetime
    end: datetime | None = None
    duration: int | None = None
    description: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "time_entries"

    def calc_duration(self) -> int | None:
        if self.end is None:
            return None
        return int((self.end - self.start).total_seconds())
