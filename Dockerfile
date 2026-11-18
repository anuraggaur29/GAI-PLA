FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -e .

# Expose port (Render sets $PORT, default to 10000)
ENV PORT=10000
EXPOSE 10000

# Start FastAPI application using the PORT env var
CMD ["sh", "-c", "uvicorn run.serve:app --host 0.0.0.0 --port ${PORT:-10000}"]
