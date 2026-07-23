#!/bin/bash
# Start backend service on port 8001

set -e

# Change to project root directory (parent of scripts/)
cd "$(dirname "$0")/.." || exit 1

# Check if server.py exists
if [ ! -f "server.py" ]; then
    echo "Error: server.py not found in $(pwd)"
    echo "Please run this script from the project root directory."
    exit 1
fi

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
elif [ -d ".venv" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
fi

# Check if uvicorn is installed
if ! command -v uvicorn &> /dev/null; then
    echo "Error: uvicorn not found"
    echo "Please install dependencies: pip install -r requirements.txt"
    exit 1
fi

echo "Starting backend service on port 8001..."
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
