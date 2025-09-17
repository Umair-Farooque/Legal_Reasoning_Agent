# ------------------- Base Image -------------------
    FROM python:3.11-slim

    # ------------------- Set Workdir -------------------
    WORKDIR /app
    
    # ------------------- Install System Dependencies -------------------
    RUN apt-get update && apt-get install -y --no-install-recommends \
            build-essential \
            git \
            && rm -rf /var/lib/apt/lists/*
    
    # ------------------- Copy and Install Python Dependencies -------------------
    COPY requirements.txt .
    RUN pip install --upgrade pip \
        && pip install --no-cache-dir -r requirements.txt
    
    # ------------------- Copy Application Code -------------------
    COPY . .
    
    # ------------------- Expose Port (Render will use $PORT) -------------------
    EXPOSE 8000
    
    # ------------------- Command for Render -------------------
    # Render sets PORT env variable automatically
    CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port ${PORT}"]
    