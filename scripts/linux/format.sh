#!/bin/bash
set -e

# Get project root directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Run Python format script
python "$PROJECT_ROOT/scripts/python/format.py" "$@"
