from datetime import datetime

from pydantic import BaseModel

from app.schemas.common import DocumentRead


class ProjectCreate(BaseModel):
    workspace_id: str
    name: str
    description: str | None = None
    color: str | None = None
    is_billable: bool = False


class ProjectUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    color: str | None = None
    is_billable: bool | None = None


class ProjectRead(DocumentRead):
    workspace_id: str
    name: str
    description: str | None = None
    color: str | None = None
    is_billable: bool
    created_at: datetime
