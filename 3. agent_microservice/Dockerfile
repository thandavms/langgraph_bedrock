FROM python:3.9-slim

WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy service code
COPY ./service ./service

# Set Python path
ENV PYTHONPATH=/app

# Expose port for FastAPI
EXPOSE 8000

# Health check for FastAPI
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Command to run the FastAPI service
CMD ["uvicorn", "service.fastapi:app", "--host", "0.0.0.0", "--port", "8000"]
