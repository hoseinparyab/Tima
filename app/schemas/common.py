from typing import Any

from bson import ObjectId
from pydantic import BaseModel, ConfigDict, field_validator


class DocumentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str

    @field_validator("id", mode="before")
    @classmethod
    def coerce_id(cls, value: Any) -> str:
        if isinstance(value, ObjectId):
            return str(value)
        return str(value)
