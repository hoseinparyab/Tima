from datetime import datetime

from pydantic import BaseModel

from app.schemas.common import DocumentRead


class TimeEntryStart(BaseModel):
    project_id: str
    description: str = ""


class TimeEntryUpdate(BaseModel):
    project_id: str | None = None
    start: datetime | None = None
    end: datetime | None = None
    description: str | None = None


class TimeEntryRead(DocumentRead):
    user_id: str
    project_id: str
    start: datetime
    end: datetime | None = None
    duration: int | None = None
    description: str
    created_at: datetime
