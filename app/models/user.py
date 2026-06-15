from datetime import datetime
from enum import Enum

from beanie import Document, Indexed, Link
from pydantic import EmailStr, Field


class UserRole(str, Enum):
    ADMIN = "admin"
    MEMBER = "member"


class User(Document):
    email: Indexed(EmailStr, unique=True)
    full_name: str
    hashed_password: str
    role: UserRole = UserRole.MEMBER
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "users"
