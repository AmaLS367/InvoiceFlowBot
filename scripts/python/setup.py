#!/usr/bin/env python3
"""Setup script for InvoiceFlowBot project.

Installs the package in editable mode with development dependencies.
Creates .env file from .env.example if it doesn't exist.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path


def get_project_root() -> Path:
    """Get the project root directory."""
    script_dir = Path(__file__).parent
    return script_dir.parent.parent


def install_dependencies() -> None:
    """Install package in editable mode with dev dependencies."""
    project_root = get_project_root()
    os.chdir(project_root)

    print("Installing package in editable mode with dev dependencies...")
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "-e", ".[dev]"],
        cwd=project_root,
    )

    if result.returncode != 0:
        print("Error: Failed to install dependencies", file=sys.stderr)
        sys.exit(1)

    print("✓ Dependencies installed successfully")


def create_env_file() -> None:
    """Create .env file from .env.example if it doesn't exist."""
    project_root = get_project_root()
    env_file = project_root / ".env"
    env_example = project_root / ".env.example"

    if env_file.exists():
        print(f"✓ .env file already exists at {env_file}")
        return

    if not env_example.exists():
        print(f"⚠ Warning: .env.example not found at {env_example}")
        return

    shutil.copy(env_example, env_file)
    print(f"✓ Created .env file from .env.example at {env_file}")
    print("⚠ Please edit .env file with your actual tokens!")


def main() -> None:
    """Main setup function."""
    project_root = get_project_root()
    os.chdir(project_root)

    print(f"Setting up InvoiceFlowBot in {project_root}")
    print("-" * 50)

    install_dependencies()
    create_env_file()

    print("-" * 50)
    print("Setup completed successfully!")


if __name__ == "__main__":
    main()
