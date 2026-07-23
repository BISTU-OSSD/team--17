#!/bin/bash
# Start backend service on port 8001

set -e

# Change to project root directory (parent of scripts/)
cd "$(dirname "$0")/.." || exit 1

# Check if server.py exists
if [ ! -f "server.py" ]; then
    echo "Error: server.py not found in $(pwd)" >&2
    echo "Please run this script from the project root directory." >&2
    exit 1
fi

# Activate virtual environment if it exists
if [ -f "venv/bin/activate" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
elif [ -f ".venv/bin/activate" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
else
    echo "Warning: No virtual environment found. Using system Python." >&2
fi

# Check if uvicorn is installed
if ! command -v uvicorn &> /dev/null; then
    echo "Error: uvicorn not found" >&2
    echo "Please install dependencies: pip install -r requirements.txt" >&2
    exit 1
fi

echo "Starting backend service on port 8001..."
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
