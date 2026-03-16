# Use official Python 3.10 slim image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies (Tesseract OCR and libGL for OpenCV/PIL)
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-uzb \
    tesseract-ocr-rus \
    tesseract-ocr-ara \
    tesseract-ocr-eng \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    libpng-dev \
    libjpeg-dev \
    zlib1g-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# python → python3 (Railway yoki Procfile da `python` ishlatilsa ham ishlaydi)
RUN ln -sf $(which python3) /usr/bin/python

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Ensure Procfile and other configs don't interfere by setting the CMD here
# This will be the default start command
CMD ["python3", "main.py"]
