#!/bin/bash

# Test Python 3.13.1 for Linux x86_64
echo ">> Test Python 3.13.1 for Linux x86_64"

## Moving to Python Directory
cd ..
cd python_compile/
cd python_linux_x86_64/

## Test Python
echo "	- Testing Python"
TEMP_PYTHON_FILE="temp_script.py"
cat <<EOF > $TEMP_PYTHON_FILE
import math
print("Math constant e:", math.e)
EOF
./bin/python3 $TEMP_PYTHON_FILE >> /dev/null 2>> /dev/null
if [ $? -eq 0 ]; then
    echo "		- Python execution test passed ✅"
else
    echo "		- Python execution not test passed ❌"
fi

## Remove unnecessary files
rm -f $TEMP_PYTHON_FILE

echo ">> Python 3.13.1 testing for Linux x86_64 completed"
