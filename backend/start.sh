#!/bin/bash
set -e

# Change to backend directory
cd backend

# Run database initialization
echo "Creating database tables..."
python init_db.py

# Start Celery worker in the background
echo "Starting Celery worker..."
celery -A app.workers.tasks worker --pool=solo --loglevel=info &

# Start FastAPI server
echo "Starting FastAPI server..."
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
