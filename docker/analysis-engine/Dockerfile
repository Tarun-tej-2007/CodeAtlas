FROM python:3.12-slim

# Set environment variables for optimized execution
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/home/appuser/.local/bin:$PATH"

# Set working directory inside container
WORKDIR /app

# Create a non-root user and group for security
RUN groupadd -g 10001 appgroup && \
    useradd -u 10001 -g appgroup -m -s /sbin/nologin appuser

# Install and cache dependencies first
COPY analysis-engine/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy source code with non-root user permissions
COPY --chown=appuser:appgroup analysis-engine/ .

# Switch to the non-root user
USER appuser

# Expose port 8001
EXPOSE 8001

# Default production command
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8001}"]
