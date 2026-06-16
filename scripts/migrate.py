import argparse
import asyncio
import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from beanie.executors.migrate import MigrationSettings, run_migrate
from beanie.migrations.models import RunningDirections

logging.basicConfig(format="%(message)s", level=logging.INFO)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Beanie database migrations")
    direction = parser.add_mutually_exclusive_group()
    direction.add_argument(
        "--forward",
        action="store_const",
        const=RunningDirections.FORWARD,
        dest="direction",
        help="Run forward migrations (default)",
    )
    direction.add_argument(
        "--backward",
        action="store_const",
        const=RunningDirections.BACKWARD,
        dest="direction",
        help="Run backward migrations",
    )
    parser.set_defaults(direction=RunningDirections.FORWARD)
    parser.add_argument(
        "-d",
        "--distance",
        type=int,
        default=0,
        help="Number of migrations to run (0 = all)",
    )
    return parser.parse_args()


async def main() -> None:
    from app.core.config import settings

    args = parse_args()
    await run_migrate(
        MigrationSettings(
            connection_uri=settings.mongodb_url,
            database_name=settings.mongodb_db,
            path=ROOT / "migrations",
            direction=args.direction,
            distance=args.distance,
            use_transaction=False,
        )
    )


if __name__ == "__main__":
    asyncio.run(main())
