#!/bin/bash

# Check if a directory argument was provided
if [ -z "$1" ]; then
    echo "Error: You must specify a workspace directory."
    echo "Usage: $0 /path/to/workspace"
    exit 1
fi

WORKSPACE_DIR="$1"

# Check if the Docker image 'ubuntu-2404' exists, if not, build it
if ! docker image inspect ubuntu-2404 > /dev/null 2>&1; then
    docker build -t ubuntu-2404 -f images/level\ 0/Dockerfile.ubuntu-2404 . > /dev/null 2>&1
    if [ $? -ne 0 ]; then
        echo "Error: Failed to build Docker image 'ubuntu-2404'."
        exit 1
    fi
fi

# Check if the Docker image 'pookie' exists, if not, build it
if ! docker image inspect pookie > /dev/null 2>&1; then
    docker build -t pookie -f images/level\ 1/Dockerfile.pookie . > /dev/null 2>&1
    if [ $? -ne 0 ]; then
        echo "Error: Failed to build Docker image 'pookie'."
        exit 1
    fi
fi

# Run the Docker container
docker run -it --rm \
    -v "$WORKSPACE_DIR":/workspace \
    -e WORKSPACE_PWD="$WORKSPACE_DIR" \
    -w /workspace \
    -v /var/run/docker.sock:/var/run/docker.sock \
    --network host \
    pookie "${@:2}"