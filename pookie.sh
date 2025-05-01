#!/bin/bash

# Parse arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --workspace)
            WORKSPACE_DIR="$2"
            shift 2
            ;;
        *)
            ARGS+=("$1")
            shift
            ;;
    esac
done

# Check if WORKSPACE_DIR is set
if [ -z "$WORKSPACE_DIR" ]; then
    echo "Error: You must specify a workspace directory using --workspace"
    echo "Usage: $0 --workspace /path/to/workspace [OTHER_ARGUMENTS]"
    exit 1
fi

echo ">> Creating pookie docker image"

# Check if Docker images exist and build if necessary
if ! docker image inspect win-macosx-pookie-lvl1-base > /dev/null 2>&1; then
    docker build -t win-macosx-pookie-lvl1-base -f images/win-macosx-pookie/Dockerfile.win-macosx-pookie-lvl1-base . > /dev/null 2>&1
    if [ $? -ne 0 ]; then
        echo "Error: Failed to build Docker image 'win-macosx-pookie-lvl1-base'."
        exit 1
    fi
fi

if ! docker image inspect win-macosx-pookie-lvl2-pookie > /dev/null 2>&1; then
    docker build -t win-macosx-pookie-lvl2-pookie -f images/win-macosx-pookie/Dockerfile.win-macosx-pookie-lvl2-pookie . > /dev/null 2>&1
    if [ $? -ne 0 ]; then
        echo "Error: Failed to build Docker image 'win-macosx-pookie-lvl2-pookie'."
        exit 1
    fi
fi

# Run Docker container with provided arguments
docker run -it --rm \
    -v "$WORKSPACE_DIR":/workspace \
    -e WORKSPACE_PWD="$WORKSPACE_DIR" \
    -w /workspace \
    -v /var/run/docker.sock:/var/run/docker.sock \
    --network host \
    win-macosx-pookie-lvl2-pookie "${ARGS[@]}"
