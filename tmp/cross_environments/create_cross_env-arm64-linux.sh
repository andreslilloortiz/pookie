#!/bin/bash

# ------------------------------------------------------
# Crossenv Terminology:
# 
# Host:
#   The machine you are building for. (Example: Android, iOS, or other embedded systems.)
#
# Build:
#   The machine you are building on. (Probably your desktop computer.)
#
# Host-python:
#   The compiled Python binary and libraries that will run on the Host system.
#
# Build-python:
#   The compiled Python binary and libraries that run on the Build system.
#
# Cross-python:
#   Build-python, specifically configured to compile packages that can run 
#   with Host-python. This script creates Cross-python.
# ------------------------------------------------------

echo ">> Create Python 3.13.1 cross enviroment for Linux ARM64"

# Define paths to Build Python and Host Python
cd ..
BUILD_PYTHON=$(pwd)/python_compile/python-3.13-x86_64-linux/bin/python3
HOST_PYTHON=$(pwd)/python_compile/python-3.13-arm64-linux/bin/python3
CROSSENV_DIR="cross_env_linux_arm64"
cd cross_environments

# Check if the cross environment directory exists and remove it if necessary
if [ -d "$CROSSENV_DIR" ]; then
    rm -rf "$CROSSENV_DIR"
fi

# Install crossenv using the Build Python's pip
echo "	- Installing crossenv"
$BUILD_PYTHON -m pip install crossenv > /dev/null 2> /dev/null

# Create a cross-compilation virtual environment with crossenv
echo "	- Creating the virtual environment"
$BUILD_PYTHON -m crossenv $HOST_PYTHON $CROSSENV_DIR

# Activate the cross-compilation virtual environment
source ./$CROSSENV_DIR/bin/activate

echo ">> The cross-compilation virtual environment is created in cross_env_linux_arm64."

# Execute with source ./crear_entorno_cruzado_aarch64.sh so the environment is created in the terminal
