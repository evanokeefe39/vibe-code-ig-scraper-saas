# syntax=docker/dockerfile:1
FROM python:3.10-slim

# Install system dependencies if needed (e.g., for psycopg)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir poetry

WORKDIR /app

# Copy dependency files FIRST for better caching
COPY pyproject.toml poetry.lock ./

# Install dependencies with cache optimization
RUN poetry config virtualenvs.create false \
    && poetry install --only main --no-root --no-interaction --no-ansi \
    && rm -rf /root/.cache/pypoetry

# Copy source code LAST so it doesn't invalidate dependency layer
COPY . .

# Collect static files during build
RUN python manage.py collectstatic --noinput --clear

# Create non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Run migrations and start server
CMD ["sh", "-c", "python manage.py migrate && gunicorn vibe_scraper.wsgi:application --bind 0.0.0.0:8000 --workers 2 --timeout 120 --max-requests 1000 --max-requests-jitter 100 --keep-alive 2"]