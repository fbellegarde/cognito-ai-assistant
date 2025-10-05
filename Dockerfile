# D:\cognito_ai_assistant\Dockerfile

# 1. Base Image: Use a slim version of Python 3.12 for smaller image size
FROM python:3.12-slim

# 2. Environment Variables
ENV PYTHONUNBUFFERED 1
ENV APP_HOME=/app

# 3. Create and Set Working Directory
RUN mkdir $APP_HOME
WORKDIR $APP_HOME

# 4. Install Dependencies
# Copy requirements first to leverage Docker layer caching
COPY requirements.txt .
# System dependencies for Gunicorn and psycopg2-binary (for Postgres/RDS later)
# Note: psycopg2-binary is free and simpler for local setup than psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy Application Code
COPY . $APP_HOME

# 6. Run Migrations & Collect Static Files (prepare the environment)
# These commands are run at build time.
RUN python manage.py collectstatic --noinput
# Note: Database migrations will be run by the entrypoint script at runtime

# 7. Expose Port
EXPOSE 8000

# 8. Run the application using Gunicorn (production WSGI server)
# CMD ["gunicorn", "cognito_assistant.wsgi:application", "--bind", "0.0.0.0:8000"]
# Use a proper entrypoint script to handle migrations at runtime, which is safer.

ENTRYPOINT ["/app/docker-entrypoint.sh"]