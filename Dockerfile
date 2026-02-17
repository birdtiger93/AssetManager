# Backend Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies (gcc might be needed for some python packages)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY config/ ./config/
# We don't copy data/ because it should be a volume
# But we need to ensure the directory exists
RUN mkdir -p data

# Environment variables
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "src.web.app:app", "--host", "0.0.0.0", "--port", "8000"]
