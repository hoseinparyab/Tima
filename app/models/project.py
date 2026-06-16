from datetime import datetime

from beanie import Document
from pydantic import Field


class Project(Document):
    workspace_id: str
    name: str
    description: str | None = None
    color: str | None = None
    is_billable: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "projects"
