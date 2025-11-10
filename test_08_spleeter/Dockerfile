FROM python:3.9-slim

# Install dependencies
RUN apt-get update && apt-get install -y ffmpeg && \
    pip install spleeter && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /data

# Default to bash
ENTRYPOINT ["/bin/bash"]
