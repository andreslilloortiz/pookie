#!/bin/bash

# Test Python 3.13.1 for Linux ARM64
echo ">> Test Python 3.13.1 for Linux ARM64"

## Install dependencies
echo "	- Installing dependencies"
sudo apt update >> /dev/null 2>> /dev/null
sudo apt install qemu-user qemu-user-static >> /dev/null 2>> /dev/null

## Moving to Python Directory
cd ..
cd python_compile/
cd python_linux_arm64/

## Test Python with Qemu
echo "	- Testing Python with Qemu"
TEMP_PYTHON_FILE="temp_script.py"
cat <<EOF > $TEMP_PYTHON_FILE
import math
print("Math constant e:", math.e)
EOF
LD_LIBRARY_PATH=./lib QEMU_LD_PREFIX=/usr/aarch64-linux-gnu qemu-aarch64-static ./bin/python3 $TEMP_PYTHON_FILE >> /dev/null 2>> /dev/null
if [ $? -eq 0 ]; then
    echo "		- Python execution test passed ✅"
else
    echo "		- Python execution not test passed ❌"
fi

## Remove unnecessary files
rm -f $TEMP_PYTHON_FILE

echo ">> Python 3.13.1 testing for Linux ARM64 completed"
