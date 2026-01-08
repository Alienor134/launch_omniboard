FROM python:3.11-slim

# Install Docker CLI (needed to spawn Omniboard containers)
RUN apt-get update && \
    apt-get install -y \
    docker.io \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY src/ ./src/

# Set environment variables
ENV PORT=8060
ENV DOCKER_MODE=true
ENV PYTHONUNBUFFERED=1

# Expose the port
EXPOSE 8060

# Run the application
CMD ["python", "src/main.py"]
