#!/bin/bash

# Compile Python 3.13.1 for Windows x86_64
echo ">> Compile Python 3.13.1 for Windows x86_64"

## Download and Install Wine
echo "	- Installing Wine"

### Enable 32-bit architecture
sudo dpkg --add-architecture i386

### Repository key
sudo mkdir -pm755 /etc/apt/keyrings
wget -O - https://dl.winehq.org/wine-builds/winehq.key | sudo gpg --dearmor -o /etc/apt/keyrings/winehq-archive.key -

### Add the repository
sudo wget -NP /etc/apt/sources.list.d/ https://dl.winehq.org/wine-builds/ubuntu/dists/jammy/winehq-jammy.sources
sudo apt update

### Install Wine
sudo apt install --install-recommends winehq-stable
winecfg

## Download Python
echo "	- Downloading Python"
wget https://www.python.org/ftp/python/3.13.1/python-3.13.1-amd64.exe

## Install Python
echo "	- Installing Python"
mkdir python_windows_x86_64
wine python-3.13.1-amd64.exe

## Remove unnecessary files
rm python-3.13.1-amd64.exe

echo ">> Python 3.13.1 compilation and installation for Windows x86_64 completed"
