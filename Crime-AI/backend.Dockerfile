FROM python:3.12-slim

WORKDIR /app

# System packages for ffmpeg + opencv headless
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libgl1 \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire project (including /backend folder)
COPY . .

# Ensure shared dirs
RUN mkdir -p /app/uploads /app/results

EXPOSE 8000

# Default for backend container
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
