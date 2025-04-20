#!/bin/bash

docker run -it --rm \
    -v $(pwd)/workspace:/workspace \
    -e WORKSPACE_PWD=$(pwd)/workspace \
    -w /workspace \
    -v /var/run/docker.sock:/var/run/docker.sock \
    pookie "$@"
