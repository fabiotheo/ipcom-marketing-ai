# syntax=docker/dockerfile:1

# Use a slim Python base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy dependency files first for better layer caching
COPY requirements.txt ./

# Install dependencies using pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY src/ ./src/
COPY pyproject.toml ./

# Expose the port used by the application
EXPOSE 8000

# Define the command to run the application
CMD ["python", "src/osp_marketing_tools/server.py"]