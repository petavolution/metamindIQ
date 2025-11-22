#!/bin/bash
# Script to run test modules with the correct Python path

# Get the absolute path to the project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Export the PYTHONPATH to include the project root
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"

# Run the test module script with the provided arguments
python3 "$PROJECT_ROOT/tests/test_modules.py" "$@" 