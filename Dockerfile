# Use Python 3.11 slim image for smaller size
FROM python:3.11-slim

# # Install system dependencies including nsjail
RUN apt-get update && apt-get install -y \
    build-essential \
    pkg-config \
    libnl-3-dev \
    libnl-route-3-dev \
    libprotobuf-dev \
    protobuf-compiler \
    autoconf \
    bison \
    flex \
    libtool \
    git \
    sudo \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install nsjail from source with specific configuration for Cloud Run
RUN git clone https://github.com/google/nsjail.git /tmp/nsjail \
    && cd /tmp/nsjail \
    && make \
    && cp nsjail /usr/local/bin/ \
    && chmod +sx /usr/local/bin/nsjail \
    && rm -rf /tmp/nsjail

# Set up sandbox environment
RUN mkdir -p /tmp/sandbox && \
    chmod 777 /tmp/sandbox && \
    mkdir -p /sys/fs/cgroup && \
    chmod 777 /sys/fs/cgroup

# Create app directory and set permissions
WORKDIR /app
RUN chmod 777 /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install -r requirements.txt

# Copy application code
COPY app.py .
COPY config.py .
COPY routes.py .
COPY validator.py .
COPY sandbox.py .
COPY exceptions.py .
COPY entrypoint.sh .

# Make entrypoint script executable
RUN chmod +x entrypoint.sh

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    echo "appuser ALL=(ALL) NOPASSWD: /bin/cp, /bin/chmod, /usr/local/bin/nsjail" >> /etc/sudoers

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8080

# Set entrypoint
ENTRYPOINT ["./entrypoint.sh"]
