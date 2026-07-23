#!/bin/bash
# Start backend service on port 8001
echo "Starting backend service on port 8001..."
uvicorn server:app --host 0.0.0.0 --port 8001 --reload