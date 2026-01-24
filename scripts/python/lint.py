#!/usr/bin/env python3
"""Linting script for InvoiceFlowBot.

Runs ruff check and mypy type checking.
"""

import os
import subprocess
import sys
from pathlib import Path


def get_project_root() -> Path:
    """Get the project root directory."""
    script_dir = Path(__file__).parent
    return script_dir.parent.parent


def run_ruff() -> bool:
    """Run ruff check.

    Returns:
        True if ruff check passed, False otherwise.
    """
    project_root = get_project_root()
    os.chdir(project_root)

    print("Running ruff check...")
    result = subprocess.run(
        [sys.executable, "-m", "ruff", "check", "."],
        cwd=project_root,
    )

    if result.returncode != 0:
        print("✗ Ruff check failed", file=sys.stderr)
        return False

    print("✓ Ruff check passed")
    return True


def run_mypy() -> bool:
    """Run mypy type checking.

    Returns:
        True if mypy passed, False otherwise.
    """
    project_root = get_project_root()
    os.chdir(project_root)

    print("Running mypy type checking...")
    result = subprocess.run(
        [sys.executable, "-m", "mypy", "backend/"],
        cwd=project_root,
    )

    if result.returncode != 0:
        print("✗ Mypy type checking failed", file=sys.stderr)
        return False

    print("✓ Mypy type checking passed")
    return True


def main() -> None:
    """Main lint function."""
    project_root = get_project_root()
    os.chdir(project_root)

    print("Running linting checks...")
    print("-" * 50)

    ruff_ok = run_ruff()
    mypy_ok = run_mypy()

    print("-" * 50)

    if not ruff_ok or not mypy_ok:
        print("✗ Linting failed", file=sys.stderr)
        sys.exit(1)

    print("✓ All linting checks passed")


if __name__ == "__main__":
    main()
