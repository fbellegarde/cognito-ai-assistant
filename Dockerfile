# Use the official Python image as the base
FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=cognito_ai_assistant.settings
# CRITICAL: Ensure the application directory is in the Python path
ENV PYTHONPATH=/app

# Set working directory for the application
WORKDIR /app

# 1. Install system dependencies (e.g., for psycopg2)
# We use 'build-essential' for compiling dependencies like psycopg2-binary
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 2. Copy and install Python dependencies FIRST (for Docker layer caching)
COPY requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt \
    && rm /tmp/requirements.txt

# 3. Copy the rest of the application code
COPY . /app

# 4. Collect static files
# This step requires the fix in manage.py to correctly locate settings.
RUN python manage.py collectstatic --noinput

# 5. The application runs on port 8000
EXPOSE 8000

# 6. Define the entrypoint script
ENTRYPOINT ["/app/docker-entrypoint.sh"]
