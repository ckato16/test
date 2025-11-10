FROM python:3.10-slim

WORKDIR /app

# --- System dependencies for audio processing ---
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# --- Copy app code ---
COPY . .

# --- Install Python dependencies (CPU-only) ---
RUN pip install --upgrade pip
RUN pip install --no-cache-dir \
    flask \
    basic-pitch \
    tensorflow==2.12.0 \
    librosa \
    numpy \
    scipy

EXPOSE 5000

CMD ["python", "server.py"]
