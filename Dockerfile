# Production-ready Dockerfile for Tallow & Co. Flask Application
# Multi-stage build for smaller final image size

# Stage 1: Builder - Install dependencies
FROM python:3.11-slim as builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies required for Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create and set working directory
WORKDIR /app

# Copy requirements first (for better layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --user --no-warn-script-location -r requirements.txt


# Stage 2: Runtime - Final lightweight image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_ENV=production \
    PATH=/home/flaskuser/.local/bin:$PATH

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd -m -u 1000 flaskuser && \
    mkdir -p /app && \
    chown -R flaskuser:flaskuser /app

# Set working directory
WORKDIR /app

# Copy Python dependencies from builder stage to flaskuser's home
COPY --from=builder --chown=flaskuser:flaskuser /root/.local /home/flaskuser/.local

# Copy application code
COPY --chown=flaskuser:flaskuser . .

# Copy and set permissions for entrypoint scripts
COPY --chown=flaskuser:flaskuser entrypoint.sh /app/entrypoint.sh
COPY --chown=flaskuser:flaskuser railway-entrypoint.sh /app/railway-entrypoint.sh
RUN chmod +x /app/entrypoint.sh /app/railway-entrypoint.sh

# Switch to non-root user
USER flaskuser

# Expose port (Railway will use $PORT env var)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

# For Railway: use railway-entrypoint.sh
# For Docker Compose: use entrypoint.sh
# Railway can override via startCommand in railway.toml
ENTRYPOINT ["/app/railway-entrypoint.sh"]
