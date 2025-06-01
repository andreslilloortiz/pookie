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
        --python-version)
            PYTHON_VERSION="$2"
            shift; shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Validate required arguments
if [ -z "$WORKSPACE" ] || [ -z "$BUILD_CMD" ] || [ -z "$TEST_CMD" ] || [ -z "$PYTHON_VERSION" ]; then
    echo "Usage: $0 --workspace <path> --build <build_command> --test <test_command> --python-version <minor_version>"
    exit 1
fi

# Variables
DIST_DIR="$WORKSPACE/dist"
PACKAGE_NAME=$(basename "$WORKSPACE")
BASE_WHEEL="${PACKAGE_NAME}-cp3$PYTHON_VERSION-cp3$PYTHON_VERSION"

echo ">> Configuration"
echo "- workspace: $WORKSPACE"
echo "- wheel base: $BASE_WHEEL"
echo "- build command: $BUILD_CMD"
echo "- test command: $TEST_CMD"

CLEAN="./pookie.sh --workspace \"$WORKSPACE\" --clean"

SECONDS=0

# -------------------------------------------------
# Build and test for all targets
# -------------------------------------------------
echo ">> Build and test for all targets"

CMD1="./pookie.sh \
    --workspace \"$WORKSPACE\" \
    --build \"$BUILD_CMD\" \
    --test \"$TEST_CMD\" \
    --python-version $PYTHON_VERSION"

eval $CLEAN > "$WORKSPACE/pookie.log" 2>&1
eval $CMD1 >> "$WORKSPACE/pookie.log" 2>&1

FILES1=(
    "$BASE_WHEEL-manylinux2014_x86_64.manylinux_2_17_x86_64.whl"
    "$BASE_WHEEL-manylinux2014_aarch64.manylinux_2_17_aarch64.whl"
    "$BASE_WHEEL-manylinux2014_armv7l.manylinux_2_17_armv7l.whl"
    "$BASE_WHEEL-manylinux2014_ppc64le.manylinux_2_17_ppc64le.whl"
    "$BASE_WHEEL-manylinux2014_s390x.manylinux_2_17_s390x.whl"
    "$BASE_WHEEL-musllinux_1_2_x86_64.whl"
    "$BASE_WHEEL-win_amd64.whl"
    "$BASE_WHEEL-macosx_11_0_x86_64.whl"
    "$BASE_WHEEL-macosx_11_0_arm64.whl"
)

for FILE in "${FILES1[@]}"; do
    if [ -f "$DIST_DIR/$FILE" ]; then
        echo "${GREEN}$FILE was successfully built and is present in dist dir${NC}"
    else
        echo "${RED}$FILE is missing so build may have failed${NC}"
    fi
done

awk '
{
  if ($0 ~ />> Testing/) {
    in_block = 1
  }

  if (in_block && $0 ~ />>/ && $0 !~ />> Testing/ && seen_testing) {
    in_block = 0
    next
  }

  if (in_block) {
    print
    if ($0 ~ />> Testing/) {
      seen_testing = 1
    }
  }
}
'  "$WORKSPACE/pookie.log"

# -------------------------------------------------
# Build and test for linux x86_64 with clang
# -------------------------------------------------
echo ">> Build and test for linux x86_64 with clang"

CMD3="./pookie.sh \
    --workspace \"$WORKSPACE\" \
    --target manylinux_2_17_x86_64 musllinux_1_2_x86_64 \
    --build \"$BUILD_CMD\" \
    --test \"$TEST_CMD\" \
    --python-version $PYTHON_VERSION \
    --linux-x86_64-compiler clang"

eval $CLEAN >> "$WORKSPACE/pookie.log" 2>&1
eval $CMD3 >> "$WORKSPACE/pookie.log" 2>&1

FILES2=(
    "$BASE_WHEEL-manylinux2014_x86_64.manylinux_2_17_x86_64.whl"
    "$BASE_WHEEL-musllinux_1_2_x86_64.whl"
)

for FILE in "${FILES2[@]}"; do
    if [ -f "$DIST_DIR/$FILE" ]; then
        echo "${GREEN}$FILE was successfully built and is present in dist dir${NC}"
    else
        echo "${RED}$FILE is missing so build may have failed${NC}"
    fi
done

awk '
{
  if ($0 ~ />> Testing/) {
    in_block = 1
  }

  if (in_block && $0 ~ />>/ && $0 !~ />> Testing/ && seen_testing) {
    in_block = 0
    next
  }

  if (in_block) {
    print
    if ($0 ~ />> Testing/) {
      seen_testing = 1
    }
  }
}
'  "$WORKSPACE/pookie.log"

# -------------------------------------------------
# Build and test for linux non native in emulate mode
# -------------------------------------------------
echo ">> Build for linux non native in emulate mode"

CMD4="./pookie.sh \
    --workspace \"$WORKSPACE\" \
    --target manylinux_2_17_aarch64 manylinux_2_17_armv7l manylinux_2_17_ppc64le manylinux_2_17_s390x \
    --build \"$BUILD_CMD\" \
    --test \"$TEST_CMD\" \
    --python-version $PYTHON_VERSION \
    --linux-non-native-mode emulate"

eval $CLEAN >> "$WORKSPACE/pookie.log" 2>&1
eval $CMD4 >> "$WORKSPACE/pookie.log" 2>&1

FILES3=(
    "$BASE_WHEEL-manylinux2014_aarch64.manylinux_2_17_aarch64.whl"
    "$BASE_WHEEL-manylinux2014_armv7l.manylinux_2_17_armv7l.whl"
    "$BASE_WHEEL-manylinux2014_ppc64le.manylinux_2_17_ppc64le.whl"
    "$BASE_WHEEL-manylinux2014_s390x.manylinux_2_17_s390x.whl"
)

for FILE in "${FILES3[@]}"; do
    if [ -f "$DIST_DIR/$FILE" ]; then
        echo "${GREEN}$FILE was successfully built and is present in dist dir${NC}"
    else
        echo "${RED}$FILE is missing so build may have failed${NC}"
    fi
done

awk '
{
  if ($0 ~ />> Testing/) {
    in_block = 1
  }

  if (in_block && $0 ~ />>/ && $0 !~ />> Testing/ && seen_testing) {
    in_block = 0
    next
  }

  if (in_block) {
    print
    if ($0 ~ />> Testing/) {
      seen_testing = 1
    }
  }
}
'  "$WORKSPACE/pookie.log"

# End of tests
echo ">> Cleaning workspace"
eval $CLEAN >> "$WORKSPACE/pookie.log" 2>&1

MINUTES=$(( SECONDS / 60 ))
REMAINING=$(( SECONDS % 60 ))
echo ">> All test completed in $MINUTES minutes and $REMAINING seconds."