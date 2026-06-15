from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TimeEntryBase(BaseModel):
    description: str
    start_time: datetime
    end_time: datetime | None = None
    team_id: str | None = None


class TimeEntryCreate(TimeEntryBase):
    pass


class TimeEntryUpdate(BaseModel):
    description: str | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    team_id: str | None = None


class TimeEntryRead(TimeEntryBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    duration_minutes: int | None = None
    created_at: datetime
    updated_at: datetime
