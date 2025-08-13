FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies (optional but recommended for some ML libs)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl && \
    rm -rf /var/lib/apt/lists/*

# Copy backend files
COPY backend/ /app/backend/

# Install Python dependencies
RUN pip install --no-cache-dir -r backend/requirements.txt

# Expose FastAPI port
EXPOSE 8000

# Start Gunicorn with Uvicorn workers
CMD ["gunicorn", "backend.app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
