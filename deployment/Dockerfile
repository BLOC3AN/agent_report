FROM python:3.10-slim-buster

WORKDIR /app


# Copy requirements and install dependencies
COPY deployment/requirements.txt /app/
RUN pip install -r requirements.txt 

# Copy application code
COPY .. /app/

# Expose ports for FastAPI and Streamlit
EXPOSE 5000 8501

ENV PYTHONPATH="${PYTHONPATH}:/app"
# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5000/health || exit 1

# Use a script to start both services
COPY deployment/start.sh /app/start.sh
RUN chmod +x /app/start.sh

CMD ["/app/start.sh"]
