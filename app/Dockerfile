FROM python:3.11-slim

LABEL maintainer="Technacy Infrastructure Team"
LABEL description="AI Voice Assistant based on Vocode with Twilio and SIP support"

# Set working directory
WORKDIR /app

# Install system dependencies for Python packages and WebRTC/SIP support
RUN apt-get update && apt-get install -y \
    # Build essentials
    gcc \
    g++ \
    make \
    pkg-config \
    # Audio support
    portaudio19-dev \
    python3-dev \
    # FFmpeg libraries for PyAV (required by aiortc)
    libavformat-dev \
    libavcodec-dev \
    libavdevice-dev \
    libavutil-dev \
    libswscale-dev \
    libswresample-dev \
    libavfilter-dev \
    # Codec support for WebRTC
    libopus-dev \
    libvpx-dev \
    # SRTP for secure media
    libsrtp2-dev \
    # SSL/TLS
    libssl-dev \
    # Cleanup
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
# Install av (PyAV) separately first as it's the most problematic
RUN pip install --no-cache-dir av==10.0.0

# Then install the rest
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 voiceai && \
    chown -R voiceai:voiceai /app

USER voiceai

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8080/health')"

# Run application
CMD ["python", "main.py"]
