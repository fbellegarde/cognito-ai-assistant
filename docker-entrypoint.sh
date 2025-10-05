#!/bin/bash
# D:\cognito_ai_assistant\docker-entrypoint.sh

set -e # Exit immediately if a command exits with a non-zero status

echo "Running database migrations..."
# Note: This will attempt to connect to the database (RDS in Phase 6)
python manage.py migrate --noinput

echo "Starting Gunicorn server..."
# Start the Gunicorn server on port 8000
exec gunicorn cognito_assistant.wsgi:application --bind 0.0.0.0:8000