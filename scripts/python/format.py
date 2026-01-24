#!/usr/bin/env python3
"""Code formatting script for InvoiceFlowBot.

Runs ruff format to format code according to project style.
"""

import os
import subprocess
import sys
from pathlib import Path


def get_project_root() -> Path:
    """Get the project root directory."""
    script_dir = Path(__file__).parent
    return script_dir.parent.parent


def run_format() -> None:
    """Run ruff format."""
    project_root = get_project_root()
    os.chdir(project_root)
    
    print("Formatting code with ruff...")
    result = subprocess.run(
        [sys.executable, "-m", "ruff", "format", "."],
        cwd=project_root,
    )
    
    if result.returncode != 0:
        print("Error: Formatting failed", file=sys.stderr)
        sys.exit(1)
    
    print("✓ Code formatted successfully")


def main() -> None:
    """Main format function."""
    run_format()


if __name__ == "__main__":
    main()
