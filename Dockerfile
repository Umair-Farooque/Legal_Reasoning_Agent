# Base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first
COPY requirements.txt .

# Install dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Expose port
EXPOSE 8000

# Use environment variable for API key (pass at runtime)
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Run app with uvicorn
CMD ["uvicorn", "app:app", "--host", "127.0.0.1", "--port", "8000"]
