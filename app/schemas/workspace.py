from pydantic import BaseModel

from app.schemas.common import DocumentRead


class WorkspaceCreate(BaseModel):
    name: str


class WorkspaceRead(DocumentRead):
    name: str
    owner_id: str
    members: list[str]


class AddMemberRequest(BaseModel):
    user_id: str
