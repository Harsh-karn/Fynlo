#!/bin/bash
set -e

# Run database migrations
echo "Running migrations..."
alembic upgrade head

# Start Celery worker in the background
echo "Starting Celery worker..."
celery -A app.workers.tasks worker --loglevel=info &

# Start FastAPI server
echo "Starting FastAPI server..."
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
