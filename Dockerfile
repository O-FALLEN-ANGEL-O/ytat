# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    fonts-dejavu-core \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p scripts videos audio images temp logs assets

# Set environment variables
ENV PYTHONPATH=/app
ENV FLASK_APP=web_app.py
ENV FLASK_ENV=production

# Expose port
EXPOSE 5000

# Default command (can be overridden)
CMD ["python", "web_app.py"]
