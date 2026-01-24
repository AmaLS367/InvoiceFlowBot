#!/usr/bin/env python3
"""Test script for InvoiceFlowBot.

Runs pytest with coverage and supports filtering by markers or test paths.
"""

import os
import subprocess
import sys
from pathlib import Path


def get_project_root() -> Path:
    """Get the project root directory."""
    script_dir = Path(__file__).parent
    return script_dir.parent.parent


def run_tests(args: list[str] | None = None) -> None:
    """Run pytest with coverage.

    Args:
        args: Additional pytest arguments (e.g., ["-m", "not storage_db", "tests/test_file.py"])
    """
    project_root = get_project_root()
    os.chdir(project_root)

    pytest_cmd = [
        sys.executable,
        "-m",
        "pytest",
        "--cov=backend",
        "--cov-report=term-missing",
    ]

    if args:
        pytest_cmd.extend(args)

    print(f"Running: {' '.join(pytest_cmd)}")
    result = subprocess.run(pytest_cmd, cwd=project_root)

    if result.returncode != 0:
        print("Error: Tests failed", file=sys.stderr)
        sys.exit(1)

    print("✓ All tests passed")


def main() -> None:
    """Main test function."""
    # Get additional arguments from command line
    args = sys.argv[1:] if len(sys.argv) > 1 else None

    run_tests(args)


if __name__ == "__main__":
    main()
