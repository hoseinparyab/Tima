import argparse
import asyncio
import sys
from datetime import datetime, timedelta
from pathlib import Path
from random import choice, randint

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from beanie.odm.operators.update.general import Set

from app.core.database import close_db, connect_db
from app.dependencies import get_password_hash
from app.models.project import Project
from app.models.time_entry import TimeEntry
from app.models.user import User
from app.models.workspace import Workspace

SEED_EMAIL = "alice@example.com"
DEFAULT_PASSWORD = "password123"

PROJECT_COLORS = ["#3B82F6", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6"]
DESCRIPTIONS = [
    "Implemented API endpoints",
    "Code review and bug fixes",
    "Client meeting",
    "UI design updates",
    "Database optimization",
    "Writing documentation",
]


async def clear_data() -> None:
    await TimeEntry.delete_all()
    await Project.delete_all()
    await Workspace.delete_all()
    await User.delete_all()


async def seed(force: bool = False) -> None:
    await connect_db()

    existing = await User.find_one(User.email == SEED_EMAIL)
    if existing and not force:
        print("Seed data already exists. Use --force to recreate.")
        await close_db()
        return

    if force:
        await clear_data()

    password_hash = get_password_hash(DEFAULT_PASSWORD)

    alice = User(
        fullname="Alice Johnson",
        email="alice@example.com",
        hashed_password=password_hash,
    )
    bob = User(
        fullname="Bob Smith",
        email="bob@example.com",
        hashed_password=password_hash,
    )
    carol = User(
        fullname="Carol Davis",
        email="carol@example.com",
        hashed_password=password_hash,
    )
    await User.insert_many([alice, bob, carol])

    alice_id = str(alice.id)
    bob_id = str(bob.id)
    carol_id = str(carol.id)

    acme = Workspace(
        name="Acme Corp",
        owner_id=alice_id,
        members=[alice_id, bob_id],
    )
    startup = Workspace(
        name="Startup Hub",
        owner_id=bob_id,
        members=[bob_id, carol_id],
    )
    await Workspace.insert_many([acme, startup])

    acme_id = str(acme.id)
    startup_id = str(startup.id)

    await User.find(User.id == alice.id).update(Set({User.workspace_ids: [acme_id]}))
    await User.find(User.id == bob.id).update(Set({User.workspace_ids: [acme_id, startup_id]}))
    await User.find(User.id == carol.id).update(Set({User.workspace_ids: [startup_id]}))

    projects = [
        Project(
            workspace_id=acme_id,
            name="Website Redesign",
            description="Redesign company website",
            color=PROJECT_COLORS[0],
            is_billable=True,
        ),
        Project(
            workspace_id=acme_id,
            name="Mobile App",
            description="iOS and Android app development",
            color=PROJECT_COLORS[1],
            is_billable=True,
        ),
        Project(
            workspace_id=acme_id,
            name="Internal Tools",
            description="Admin dashboard and utilities",
            color=PROJECT_COLORS[2],
            is_billable=False,
        ),
        Project(
            workspace_id=startup_id,
            name="MVP Development",
            description="Build minimum viable product",
            color=PROJECT_COLORS[3],
            is_billable=True,
        ),
        Project(
            workspace_id=startup_id,
            name="Marketing",
            description="Social media and content",
            color=PROJECT_COLORS[4],
            is_billable=False,
        ),
    ]
    await Project.insert_many(projects)

    now = datetime.utcnow()
    time_entries: list[TimeEntry] = []

    for day_offset in range(7):
        day = now - timedelta(days=day_offset)
        for user_id in [alice_id, bob_id, carol_id]:
            entries_count = randint(1, 3)
            for _ in range(entries_count):
                project = choice(projects)
                start_hour = randint(8, 16)
                duration_seconds = randint(1800, 14400)
                start = day.replace(
                    hour=start_hour,
                    minute=randint(0, 59),
                    second=0,
                    microsecond=0,
                )
                end = start + timedelta(seconds=duration_seconds)
                entry = TimeEntry(
                    user_id=user_id,
                    project_id=str(project.id),
                    start=start,
                    end=end,
                    duration=duration_seconds,
                    description=choice(DESCRIPTIONS),
                    created_at=start,
                )
                time_entries.append(entry)

    running_project = projects[0]
    running_entry = TimeEntry(
        user_id=alice_id,
        project_id=str(running_project.id),
        start=now - timedelta(minutes=45),
        description="Active timer session",
    )
    time_entries.append(running_entry)

    await TimeEntry.insert_many(time_entries)
    await close_db()

    print("Seed data created successfully.")
    print()
    print("Test accounts (password for all: password123):")
    print("  alice@example.com  - owner of Acme Corp")
    print("  bob@example.com    - member of both workspaces")
    print("  carol@example.com  - member of Startup Hub")
    print()
    print(f"  Users:       3")
    print(f"  Workspaces:  2")
    print(f"  Projects:    {len(projects)}")
    print(f"  Time entries: {len(time_entries)} (includes 1 running timer)")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Seed database with fake data")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Delete existing data and recreate seed",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    asyncio.run(seed(force=args.force))
