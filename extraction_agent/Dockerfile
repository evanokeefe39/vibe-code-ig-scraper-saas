# ============ Build stage ============
FROM python:3.12-slim AS builder

WORKDIR /app

# Install build dependencies (only needed for some wheels)
RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

# Copy only requirements first (maximize cache)
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir --user -r requirements.txt

# ============ Final stage ============
FROM python:3.12-slim

WORKDIR /app

# Create non-root user (security best practice)
RUN adduser --disabled-password --gecos '' appuser

# Copy python packages from builder
COPY --from=builder /root/.local /home/appuser/.local

# Make sure packages are in PATH
ENV PATH=/home/appuser/.local/bin:$PATH

# Copy your code
COPY . .

# Change ownership to non-root user
RUN chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Healthcheck (optional but nice for Railway/Render)
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD ["python", "-c", "import requests; requests.get('http://localhost:8000/', timeout=2)"]

# Start the server (4 workers is perfect for CPU-bound LLM calls)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]