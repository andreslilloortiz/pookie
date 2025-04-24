#!/bin/bash

# Check if a directory argument was provided
if [ -z "$1" ]; then
    echo "Error: You must specify a workspace directory."
    echo "Usage: $0 /path/to/workspace"
    exit 1
fi

WORKSPACE_DIR="$1"

docker run -it --rm \
    -v "$WORKSPACE_DIR":/workspace \
    -e WORKSPACE_PWD="$WORKSPACE_DIR" \
    -w /workspace \
    -v /var/run/docker.sock:/var/run/docker.sock \
    pookie-launcher "${@:2}"
