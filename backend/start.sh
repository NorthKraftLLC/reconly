#!/bin/bash
# Start server (migrations handled separately)
echo "Starting server..."
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-10000}