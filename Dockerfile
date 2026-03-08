# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy project
COPY . /app/

# Make entrypoint.sh executable
RUN chmod +x entrypoint.sh

# Create a non-root user
RUN adduser --disabled-password --gecos '' django-user && chown -R django-user:django-user /app
USER django-user

# Expose port
EXPOSE 8000

# Run the application
CMD ["./entrypoint.sh"]