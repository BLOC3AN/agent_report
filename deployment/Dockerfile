# ==========================================
# deployment/Dockerfile - Agent Report Service
# ==========================================

FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY deployment/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /app/

# Set Python path
ENV PYTHONPATH="${PYTHONPATH}:/app"

# Create directories for scheduler state and logs
RUN mkdir -p /app/data /app/logs

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# Create volume for scheduler state persistence
VOLUME ["/app/data"]

# Expose port for FastAPI only (removed Streamlit)
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:5000/health || exit 1

# Copy and set permissions for start script
COPY deployment/start.sh /app/start.sh
USER root
RUN chmod +x /app/start.sh
USER app

# Start the service
CMD ["/app/start.sh"]
