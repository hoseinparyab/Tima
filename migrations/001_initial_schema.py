from beanie import free_fall_migration

from app.models.project import Project
from app.models.time_entry import TimeEntry
from app.models.user import User
from app.models.workspace import Workspace

MODELS = [User, Workspace, Project, TimeEntry]


class Forward:
    @free_fall_migration(document_models=MODELS)
    async def create_initial_schema(self, session) -> None:
        """Indexes are created automatically by Beanie before this runs."""


class Backward:
    @free_fall_migration(document_models=MODELS)
    async def drop_collections(self, session) -> None:
        for model in reversed(MODELS):
            await model.get_pymongo_collection().drop(session=session)
