#!/bin/bash

# Compile Python 3.13.2 for MacOS x86_64
echo ">> Compile Python 3.13.2 for MacOS x86_64"

## Download Darling
echo "	- Downloading Darling"
wget https://github.com/darlinghq/darling/releases/download/v0.1.20230310_update_sources_11_5/darling_0.1.20230310.jammy_amd64.deb

## Install Darling
echo "	- Installing Darling"
sudo dpkg -i darling_0.1.20230310.jammy_amd64.deb

## Download Python
echo "	- Downloading Python"
wget https://www.python.org/ftp/python/3.13.2/python-3.13.2-macos11.pkg

## Installing Python
echo "	- Installing Python"
sudo darling shell <<EOF
xcode-select --install
mkdir -p ../../compiled-python/python-3.13.2-x86_64-macos
installer -pkg python-3.13.2-macos11.pkg -target ../../compiled-python/python-3.13.2-x86_64-macos
EOF

# cp -R /Library/Frameworks/Python.framework/Versions/3.13/* ../../compiled-python/python-3.13.2-x86_64-macos

## Clean up temporary files
rm darling_0.1.20230310.jammy_amd64.deb
rm python-3.13.2-macos11.pkg

echo ">> Python 3.13.2 installation in Darling completed"
