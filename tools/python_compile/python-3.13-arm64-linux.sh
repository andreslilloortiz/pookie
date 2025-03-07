#!/bin/bash

# Compile Python 3.13.1 for Linux ARM64
echo ">> Compile Python 3.13.1 for Linux ARM64"

# Cross-compilation is performed
## Host Python: Python 3.13.1 for Linux ARM64
## Build Python: Python 3.13.1 for Linux x86_64

## Download Python
echo "	- Downloading Python"
wget https://www.python.org/ftp/python/3.13.1/Python-3.13.1.tar.xz >> /dev/null 2>> /dev/null

## Install dependencies
echo "	- Installing dependencies"
sudo apt update >> /dev/null 2>> /dev/null
sudo apt install -y gcc-aarch64-linux-gnu g++-aarch64-linux-gnu libssl-dev zlib1g-dev libncurses5-dev libncursesw5-dev libreadline-dev libsqlite3-dev libgdbm-dev libbz2-dev libexpat1-dev liblzma-dev tk-dev libffi-dev wget >> /dev/null 2>> /dev/null

## Extract the source code
echo "	- Extracting source code"
tar -xvf Python-3.13.1.tar.xz >> /dev/null 2>> /dev/null

## Build Python directory
BUILD_PYTHON=$(pwd)/python-3.13-x86_64-linux/bin/python3

## Create a virtual environment with Build Python
echo "	- Creating a virtual enviroment with Build Python"
$BUILD_PYTHON -m venv myenv313
source myenv313/bin/activate

## Create a directory for cross-compilation
cd Python-3.13.1/
mkdir build_cross
cd build_cross

## Set up environment variables for cross-compilation
echo "	- Setting up the environment"
export CC=aarch64-linux-gnu-gcc
export CXX=aarch64-linux-gnu-g++
export AR=aarch64-linux-gnu-ar
export RANLIB=aarch64-linux-gnu-ranlib

## Create a config.site file for custom configurations
echo "ac_cv_file__dev_ptmx=yes" > config.site
echo "ac_cv_file__dev_ptc=no" >> config.site

## Configure the Python build script
CONFIG_SITE=$(pwd)/config.site ../configure \
    --host=aarch64-linux-gnu \
    --build=$(../config.guess) \
    --prefix=$(pwd)/python-3.13-arm64-linux \
    --enable-shared \
    CROSS_COMPILE=aarch64-linux-gnu- \
    CFLAGS="-march=armv8-a" \
    --with-build-python=$BUILD_PYTHON \
    --disable-ipv6 >> /dev/null 2>> /dev/null

## Compile Python
echo "	- Compiling Host Python"
make -j$(nproc) >> /dev/null 2>> /dev/null

## Install Python
echo "	- Installing Host Python"
make install >> /dev/null 2>> /dev/null

## Exit the Build Python virtual environment
deactivate

## Move the compiled and installed Python to the current directory
cd ..
cd ..
mv Python-3.13.1/build_cross/python-3.13-arm64-linux/ .

## Remove unnecessary files
rm Python-3.13.1.tar.xz
rm -r Python-3.13.1
rm -r myenv313

echo ">> Python 3.13.1 compilation and installation for Linux ARM64 completed"

