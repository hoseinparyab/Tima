from pydantic import BaseModel, EmailStr

from app.schemas.common import DocumentRead


class UserBase(BaseModel):
    fullname: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserRead(UserBase, DocumentRead):
    workspace_ids: list[str]
