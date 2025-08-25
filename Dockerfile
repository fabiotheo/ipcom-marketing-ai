# syntax=docker/dockerfile:1

# Use a slim Python base image
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Copy project files
COPY requirements.txt pyproject.toml ./
COPY src/ ./src/

# Install the package and its dependencies
RUN pip install --no-cache-dir -e .

# Expose the port used by the application
EXPOSE 8000

# Define the command to run the application using the entry point
CMD ["osp_marketing_tools"]