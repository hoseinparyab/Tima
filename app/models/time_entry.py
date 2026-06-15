from datetime import datetime

from beanie import Document, Link
from pydantic import Field

from app.models.team import Team
from app.models.user import User


class TimeEntry(Document):
    user: Link[User]
    team: Link[Team] | None = None
    description: str
    start_time: datetime
    end_time: datetime | None = None
    duration_minutes: int | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "time_entries"
