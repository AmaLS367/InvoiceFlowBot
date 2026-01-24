#!/usr/bin/env python3
"""Database migration script for InvoiceFlowBot.

Runs Alembic migrations to upgrade or downgrade the database schema.
"""

import os
import subprocess
import sys
from pathlib import Path


def get_project_root() -> Path:
    """Get the project root directory."""
    script_dir = Path(__file__).parent
    return script_dir.parent.parent


def run_migration(command: str = "upgrade head") -> None:
    """Run Alembic migration command.

    Args:
        command: Alembic command (e.g., "upgrade head", "downgrade -1", "revision -m 'message'")
    """
    project_root = get_project_root()
    os.chdir(project_root)

    alembic_ini = project_root / "backend" / "alembic.ini"

    if not alembic_ini.exists():
        print(f"Error: alembic.ini not found at {alembic_ini}", file=sys.stderr)
        sys.exit(1)

    cmd_parts = command.split()
    alembic_cmd = [
        sys.executable,
        "-m",
        "alembic",
        "-c",
        str(alembic_ini),
    ] + cmd_parts

    print(f"Running: {' '.join(alembic_cmd)}")
    result = subprocess.run(alembic_cmd, cwd=project_root)

    if result.returncode != 0:
        print("Error: Migration failed", file=sys.stderr)
        sys.exit(1)

    print("✓ Migration completed successfully")


def main() -> None:
    """Main migration function."""
    if len(sys.argv) > 1:
        # Custom command provided
        command = " ".join(sys.argv[1:])
    else:
        # Default: upgrade to head
        command = "upgrade head"

    run_migration(command)


if __name__ == "__main__":
    main()
