# Use the official Python image as the base
FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE cognito_ai_assistant.settings

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
# Note: You MUST ensure 'langchain-openai' is in this file!
COPY requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt \
    && rm /tmp/requirements.txt

# 3. Copy the rest of the application code
COPY . /app

# 4. Collect static files
# This step requires all Python modules to be correctly installed.
RUN python manage.py collectstatic --noinput

# 5. The application runs on port 8000
EXPOSE 8000

# 6. Define the entrypoint script
# The script will handle database migrations and starting Gunicorn.
ENTRYPOINT ["/app/docker-entrypoint.sh"]
