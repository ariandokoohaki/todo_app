# Dockerfile
# Use an official Python runtime as a parent image
FROM python:3.13-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Install system dependencies if any (e.g., for psycopg2 or other C extensions)
# RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
# If your app is in a subdirectory (e.g., 'app_src'), adjust the COPY command.
# This example assumes your FastAPI app code is in a directory named 'app'
# at the same level as this Dockerfile.
COPY ./app /app/app
# If you have other directories like 'core', 'models', 'schemas', 'services' at the root
# that are part of your application, copy them too.
# Example:
# COPY ./core /app/core
# COPY ./models /app/models
# COPY ./schemas /app/schemas
# COPY ./services /app/services
# COPY ./main.py /app/main.py # If your main.py is at the root and imports from 'app'

# Expose the port the app runs on
EXPOSE 8000

# Define the command to run the application
# This assumes your FastAPI application instance is named 'app' in a file 'app/main.py'.
# Adjust if your entrypoint is different (e.g., 'main:app' if main.py is at root).
# Using 0.0.0.0 to bind to all interfaces, making it accessible from outside the container.
# The default port for Uvicorn is 8000.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
