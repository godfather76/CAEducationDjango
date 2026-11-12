ARG REBUILD_DATE=2026-07-01

# Start from the official lightweight Python 3.13 image
FROM python:3.13-slim

# Prevent Python from buffering stdout/stderr and writing bytecode
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Install the necessary system packages for GeoDjango
RUN apt-get update && apt-get install -y --no-install-recommends \
    binutils \
    libproj-dev \
    gdal-bin \
    libgdal-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /code

# Copy requirements and install dependencies
COPY requirements.txt /code/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of your Django project into the container
COPY . /code/