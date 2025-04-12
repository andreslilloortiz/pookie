# Use the Python 3.13 base image
FROM python:3.13-alpine

# Install necessary dependencies
RUN apk add --no-cache \
    git \
    docker-cli \
    bash

# Add pookie.py
COPY pookie.py .

# Clone repository with prebuilt python binaries
RUN git clone https://github.com/andreslilloortiz/python-prebuilt-binaries.git

# Entrypoint
ENTRYPOINT ["python", "/pookie.py"]