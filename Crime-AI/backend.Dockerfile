FROM python:3.12-slim

WORKDIR /app

# System packages for ffmpeg/opencv
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libgl1 \
 && rm -rf /var/lib/apt/lists/*

# Install deps
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . .

# Ensure uploads dir exists
RUN mkdir -p /app/uploads

EXPOSE 8000

# Default cmd: API server
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
