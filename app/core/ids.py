from bson import ObjectId
from fastapi import HTTPException, status


def ensure_valid_object_id(value: str, label: str = "Resource") -> str:
    if not ObjectId.is_valid(value):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{label} not found",
        )
    return value
