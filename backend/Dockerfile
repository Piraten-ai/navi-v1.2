# Build stage
FROM python:3.14-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    g++ \
    gcc \
    libgl1 \
    libglib2.0-0 \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy and install dependencies
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --user --no-warn-script-location -r requirements.txt

# Runtime stage
FROM python:3.14-slim

# Set labels for better container management
LABEL maintainer="aads-team" \
      version="1.0" \
      description="AADS Backend API with audio processing"

WORKDIR /app

# Install runtime dependencies only (including audio for voice system)
RUN apt-get update && apt-get install -y --no-install-recommends \
    alsa-utils \
    espeak-ng \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    libpq5 \
    libsm6 \
    libsndfile1 \
    libxext6 \
    libxrender1 \
    pulseaudio-utils \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user first
RUN useradd -m -u 1000 -s /sbin/nologin appuser

# Copy installed packages from builder and set ownership
COPY --from=builder --chown=appuser:appuser /root/.local /home/appuser/.local

# Copy application and data with proper ownership
COPY --chown=appuser:appuser app/ app/
COPY --chown=appuser:appuser data/ data/

# Create necessary directories for logs, models, and audio
RUN mkdir -p /app/logs /app/models/piper /app/audio \
    && chown -R appuser:appuser /app

# Add local bin to PATH
ENV PATH=/home/appuser/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Security: Run healthcheck as non-root
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health').read()" || exit 1

USER appuser

EXPOSE 8000

# Use exec form for proper signal handling
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "--log-level", "info"]
