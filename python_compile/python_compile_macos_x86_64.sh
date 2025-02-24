#!/bin/bash

# Compile Python 3.13.1 for MacOS x86_64
echo ">> Compile Python 3.13.1 for MacOS x86_64"

## Download Darling
echo "	- Downloading Darling"
wget https://github.com/darlinghq/darling/releases/download/v0.1.20230310_update_sources_11_5/darling_0.1.20230310.jammy_amd64.deb >> /dev/null 2>> /dev/null

## Install Darling
echo "	- Installing Darling"
sudo dpkg -i darling_0.1.20230310.jammy_amd64.deb >> /dev/null 2>> /dev/null

## Download Python
echo "	- Downloading Python"
wget https://www.python.org/ftp/python/3.13.1/Python-3.13.1.tar.xz >> /dev/null 2>> /dev/null

## Start Darling
echo "  - Starting Sarling"
darling shell

## Install dependencies
echo "	- Installing dependencies"
brew install gcc openssl readline sqlite3 xz zlib

## Remove unnecessary files
rm darling_0.1.20230310.jammy_amd64.deb
rm Python-3.13.1.tar.xz
