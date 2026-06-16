from beanie import Document
from pydantic import Field


class Workspace(Document):
    name: str
    owner_id: str
    members: list[str] = Field(default_factory=list)

    class Settings:
        name = "workspaces"
