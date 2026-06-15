from datetime import datetime

from beanie import Document, Indexed, Link
from pydantic import Field

from app.models.user import User


class Team(Document):
    name: Indexed(str, unique=True)
    description: str | None = None
    owner: Link[User]
    members: list[Link[User]] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "teams"
