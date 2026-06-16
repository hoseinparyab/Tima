import argparse
import shutil
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from beanie.migrations import template


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a new Beanie migration file")
    parser.add_argument("-n", "--name", required=True, help="Migration name")
    parser.add_argument(
        "-p",
        "--path",
        default=str(ROOT / "migrations"),
        help="Migrations directory",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    migrations_dir = Path(args.path)
    migrations_dir.mkdir(parents=True, exist_ok=True)

    existing = sorted(migrations_dir.glob("[!_]*.py"))
    next_number = 1
    if existing:
        last = existing[-1].stem.split("_", 1)[0]
        if last.isdigit():
            next_number = int(last) + 1

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    file_name = f"{next_number:03d}_{timestamp}_{args.name}.py"
    target = migrations_dir / file_name
    shutil.copy(template.__file__, target)
    print(f"Created migration: {target}")


if __name__ == "__main__":
    main()
