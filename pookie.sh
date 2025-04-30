#!/bin/bash

# Check if a directory argument was provided
if [ -z "$1" ]; then
    echo "Error: You must specify a workspace directory."
    echo "Usage: $0 /path/to/workspace ARGUMENTS"
    exit 1
fi

WORKSPACE_DIR="$1"

echo ">> Creating pookie docker image"

# Check if the Docker image 'win-macosx-pookie-lvl1-base' exists, if not, build it
if ! docker image inspect win-macosx-pookie-lvl1-base > /dev/null 2>&1; then
    docker build -t win-macosx-pookie-lvl1-base -f images/win-macosx-pookie/Dockerfile.win-macosx-pookie-lvl1-base . > /dev/null 2>&1
    if [ $? -ne 0 ]; then
        echo "Error: Failed to build Docker image 'win-macosx-pookie-lvl1-base'."
        exit 1
    fi
fi

# Check if the Docker image 'win-macosx-pookie-lvl2-pookie' exists, if not, build it
if ! docker image inspect win-macosx-pookie-lvl2-pookie > /dev/null 2>&1; then
    docker build -t win-macosx-pookie-lvl2-pookie -f images/win-macosx-pookie/Dockerfile.win-macosx-pookie-lvl2-pookie . > /dev/null 2>&1
    if [ $? -ne 0 ]; then
        echo "Error: Failed to build Docker image 'win-macosx-pookie-lvl2-pookie'."
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
    win-macosx-pookie-lvl2-pookie "${@:2}"