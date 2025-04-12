# Use the Python 3.13 base image
FROM ubuntu:latest

# Install necessary dependencies
RUN apt-get update && apt-get install -y \
    git \
    docker.io \
    python3 \
    && rm -rf /var/lib/apt/lists/*

# Add pookie.py
COPY pookie.py .

# Clone repository with prebuilt python binaries
RUN git clone https://github.com/andreslilloortiz/python-prebuilt-binaries.git

# Copy images
COPY images/Dockerfile.all-macos /Dockerfile.all-macos
COPY images/Dockerfile.all-windows /Dockerfile.all-windows
COPY images/Dockerfile.x86_64-linux /Dockerfile.x86_64-linux

# Entrypoint
ENTRYPOINT ["python3", "/pookie.py"]