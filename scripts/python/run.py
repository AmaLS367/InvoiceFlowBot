#!/usr/bin/env python3
"""Run script for InvoiceFlowBot.

Applies database migrations and starts the bot.
"""

import os
import subprocess
import sys
from pathlib import Path


def get_project_root() -> Path:
    """Get the project root directory."""
    script_dir = Path(__file__).parent
    return script_dir.parent.parent


def run_migrations() -> None:
    """Apply database migrations before starting the bot."""
    project_root = get_project_root()

    # Import migrate function from the same package
    migrate_script = project_root / "scripts" / "python" / "migrate.py"

    print("Applying database migrations...")
    result = subprocess.run(
        [sys.executable, str(migrate_script)],
        cwd=project_root,
    )

    if result.returncode != 0:
        print("Error: Failed to apply migrations", file=sys.stderr)
        sys.exit(1)

    print("✓ Migrations applied successfully")


def run_bot() -> None:
    """Start the bot."""
    project_root = get_project_root()
    bot_script = project_root / "bot.py"

    if not bot_script.exists():
        print(f"Error: bot.py not found at {bot_script}", file=sys.stderr)
        sys.exit(1)

    print("Starting bot...")
    print("-" * 50)

    # Run bot in the same process
    os.chdir(project_root)
    result = subprocess.run([sys.executable, str(bot_script)], cwd=project_root)

    sys.exit(result.returncode)


def main() -> None:
    """Main run function."""
    project_root = get_project_root()
    os.chdir(project_root)

    run_migrations()
    run_bot()


if __name__ == "__main__":
    main()
