# Use official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory to /app
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH=/app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements0.txt .

# Install python dependencies
RUN pip install --no-cache-dir -r requirements0.txt

# Copy the entire project
COPY . .

# Expose port 7860 (Hugging Face Default)
EXPOSE 7860

# Run uvicorn server on port 7860 (Running from root now)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
