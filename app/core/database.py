from beanie import init_beanie
from pymongo import AsyncMongoClient

from app.core.config import settings
from app.models.project import Project
from app.models.time_entry import TimeEntry
from app.models.user import User
from app.models.workspace import Workspace

client: AsyncMongoClient | None = None


async def connect_db() -> None:
    global client
    client = AsyncMongoClient(settings.mongodb_url)
    await init_beanie(
        database=client.get_database(settings.mongodb_db),
        document_models=[User, Workspace, Project, TimeEntry],
    )


async def close_db() -> None:
    global client
    if client is not None:
        await client.close()
        client = None
