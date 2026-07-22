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
COPY server/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy source code with non-root user permissions
COPY --chown=appuser:appgroup server/ .

# Make startup script executable
RUN chmod +x start.sh

# Switch to the non-root user
USER appuser

# Expose port 8000
EXPOSE 8000

# Default production command
CMD ["./start.sh"]
