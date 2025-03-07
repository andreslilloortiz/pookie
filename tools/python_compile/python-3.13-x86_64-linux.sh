#!/bin/bash

# Compile Python 3.13.1 for Linux x86_64
echo ">> Compile Python 3.13.1 for Linux x86_64"

## Download Python
echo "	- Downloading Python"
wget https://www.python.org/ftp/python/3.13.1/Python-3.13.1.tar.xz >> /dev/null 2>> /dev/null

## Install dependencies
echo "	- Installing dependencies"
sudo apt update >> /dev/null 2>> /dev/null
sudo apt install -y build-essential libssl-dev zlib1g-dev libncurses5-dev libncursesw5-dev libreadline-dev libsqlite3-dev libgdbm-dev libbz2-dev libexpat1-dev liblzma-dev tk-dev libffi-dev wget >> /dev/null 2>> /dev/null

## Extract the source code
echo "	- Extracting source code"
tar -xvf Python-3.13.1.tar.xz >> /dev/null 2>> /dev/null
cd Python-3.13.1/

## Set up the environment
echo "	- Setting up the environment"
./configure --prefix=$(pwd)/python-3.13-x86_64-linux --enable-optimizations >> /dev/null 2>> /dev/null

## Compile Python
echo "	- Compiling Python"
make -j$(nproc) >> /dev/null 2>> /dev/null

## Install Python
echo "	- Installing Python"
make install >> /dev/null 2>> /dev/null

# Move the compiled and installed Python to the current directory
cd ..
mv Python-3.13.1/python-3.13-x86_64-linux .

## Remove unnecessary files
rm Python-3.13.1.tar.xz
rm -r Python-3.13.1

echo ">> Python 3.13.1 compilation and installation for Linux x86_64 completed"

