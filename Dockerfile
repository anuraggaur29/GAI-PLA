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

# Hugging Face Spaces exposes port 7860
EXPOSE 7860

# Start GAI-PLA FastAPI application
CMD ["uvicorn", "run.serve:app", "--host", "0.0.0.0", "--port", "7860"]
