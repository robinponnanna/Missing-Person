# Use a slim Python image for Windows compatibility and small size
FROM python:3.12-slim

# Set environment variables for better logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copy requirements and install dependencies
# We copy this first so Docker caches the installation step
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project
COPY . .

# Expose the FastAPI port
EXPOSE 8000

# Bind to 0.0.0.0 so the Windows host can access the container's internal network
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Add this line to your Dockerfile
ENV PYTHONPATH=/app