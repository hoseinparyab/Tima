from beanie import Document, Indexed
from pydantic import EmailStr, Field


class User(Document):
    fullname: str
    email: Indexed(EmailStr, unique=True)
    hashed_password: str
    workspace_ids: list[str] = Field(default_factory=list)

    class Settings:
        name = "users"
