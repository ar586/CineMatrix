FROM python:3.10-slim

WORKDIR /app

# Install system dependencies (gcc for building some python packages)
RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend ./backend
COPY agents ./agents
COPY scripts ./scripts

# Set python path
ENV PYTHONPATH=/app

# Expose port
EXPOSE 8000

# Start command
CMD ["uvicorn", "backend.api.server:app", "--host", "0.0.0.0", "--port", "8000"]
