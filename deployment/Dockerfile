FROM python:3.10-slim-buster

WORKDIR /app


# Copy requirements and install dependencies
COPY deployment/requirements.txt /app/
RUN pip install -r requirements.txt 

# Copy application code
COPY .. /app/

# Expose the port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5000/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000"]
