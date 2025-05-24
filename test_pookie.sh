#!/bin/bash

# This file is part of pookie.

# Copyright (C) 2025 Andrés Lillo Ortiz

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

# Colors for output
RED=$'\033[0;31m'
GREEN=$'\033[0;32m'
NC=$'\033[0m'

# Argument parsing
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
    --workspace)
        WORKSPACE="$2"
        shift; shift
        ;;
    --build)
        BUILD_CMD="$2"
        shift; shift
        ;;
    --test)
        TEST_CMD="$2"
        shift; shift
        ;;
    *)
        echo "Unknown option: $1"
        exit 1
        ;;
    esac
done

# Validate required arguments
if [ -z "$WORKSPACE" ] || [ -z "$BUILD_CMD" ] || [ -z "$TEST_CMD" ]; then
    echo "Usage: $0 --workspace <path> --build <build_command> --test <test_command>"
    exit 1
fi

# Variables
DIST_DIR="$WORKSPACE/dist"
PACKAGE_NAME=$(basename "$WORKSPACE")
BASE_WHEEL="${PACKAGE_NAME}-cp311-cp311"

echo ">> Workspace: $WORKSPACE"
echo ">> Wheel base: $BASE_WHEEL"
echo ">> Build command: $BUILD_CMD"
echo ">> Test command: $TEST_CMD"

CLEAN="./pookie.sh --workspace \"$WORKSPACE\" --clean"

# -------------------------------
# BUILD
# -------------------------------
echo ">> BUILD"

CMD1="./pookie.sh \
    --workspace \"$WORKSPACE\" \
    --target manylinux_2_17_x86_64 manylinux_2_17_aarch64 musllinux_1_2_x86_64 macosx_11_0_x86_64 \
    --build \"$BUILD_CMD\" \
    --python-version 11"

eval $CLEAN >> "$WORKSPACE/pookie.log" 2>&1
eval $CMD1 >> "$WORKSPACE/pookie.log" 2>&1

FILES1=(
    "$BASE_WHEEL-manylinux_2_17_x86_64.manylinux2014_x86_64.whl"
    "$BASE_WHEEL-manylinux_2_17_aarch64.manylinux2014_aarch64.whl"
    "$BASE_WHEEL-musllinux_1_2_x86_64.whl"
    "$BASE_WHEEL-macosx_11_0_x86_64.whl"
)

echo ">> Checking general build files:"
for FILE in "${FILES1[@]}"; do
    if [ -f "$DIST_DIR/$FILE" ]; then
        echo "${GREEN}$FILE found${NC}"
    else
        echo "${RED}$FILE NOT found${NC}"
    fi
done

# -------------------------------
# TEST
# -------------------------------
echo ">> TEST"

CMD2="./pookie.sh \
    --workspace \"$WORKSPACE\" \
    --target manylinux_2_17_x86_64 manylinux_2_17_aarch64 musllinux_1_2_x86_64 \
    --build \"$BUILD_CMD\" \
    --test \"$TEST_CMD\" \
    --python-version 11"

eval $CLEAN >> "$WORKSPACE/pookie.log" 2>&1
eval $CMD2 >> "$WORKSPACE/pookie.log" 2>&1

# -------------------------------
# BUILD LINUX X86_64 WITH CLANG
# -------------------------------
echo ">> BUILD LINUX X86_64 WITH CLANG"

CMD3="./pookie.sh \
    --workspace \"$WORKSPACE\" \
    --target manylinux_2_17_x86_64 musllinux_1_2_x86_64 \
    --build \"$BUILD_CMD\" \
    --python-version 11 \
    --linux-x86_64-compiler clang"

eval $CLEAN >> "$WORKSPACE/pookie.log" 2>&1
eval $CMD3 >> "$WORKSPACE/pookie.log" 2>&1

FILES2=(
    "$BASE_WHEEL-manylinux_2_17_x86_64.manylinux2014_x86_64.whl"
    "$BASE_WHEEL-musllinux_1_2_x86_64.whl"
)

echo ">> Checking clang build files:"
for FILE in "${FILES2[@]}"; do
    if [ -f "$DIST_DIR/$FILE" ]; then
        echo "${GREEN}$FILE found${NC}"
    else
        echo "${RED}$FILE NOT found${NC}"
    fi
done

# -------------------------------
# BUILD LINUX AARCH64 EMULATE MODE
# -------------------------------
echo ">> BUILD LINUX AARCH64 EMULATE MODE"

CMD4="./pookie.sh \
    --workspace \"$WORKSPACE\" \
    --target manylinux_2_17_aarch64 \
    --build \"$BUILD_CMD\" \
    --python-version 11 \
    --linux-aarch64-mode emulate"

eval $CLEAN >> "$WORKSPACE/pookie.log" 2>&1
eval $CMD4 >> "$WORKSPACE/pookie.log" 2>&1

FILES3=(
    "$BASE_WHEEL-manylinux_2_17_aarch64.manylinux2014_aarch64.whl"
)

echo ">> Checking emulate mode build files:"
for FILE in "${FILES3[@]}"; do
    if [ -f "$DIST_DIR/$FILE" ]; then
        echo "${GREEN}$FILE found${NC}"
    else
        echo "${RED}$FILE NOT found${NC}"
    fi
done

echo ">> Cleaning workspace"
eval $CLEAN >> "$WORKSPACE/pookie.log" 2>&1

echo ">> All test completed. Check \"$WORKSPACE/pookie.log\" for details."
