from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import settings
from app.models.team import Team
from app.models.time_entry import TimeEntry
from app.models.user import User

client: AsyncIOMotorClient | None = None


async def connect_db() -> None:
    global client
    client = AsyncIOMotorClient(settings.mongodb_url)
    await init_beanie(
        database=client[settings.mongodb_db],
        document_models=[User, Team, TimeEntry],
    )


async def close_db() -> None:
    global client
    if client is not None:
        client.close()
        client = None
