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
wget https://www.python.org/ftp/python/3.13.1/python-3.13.1-macos11.pkg >> /dev/null 2>> /dev/null

## Installing Python
echo "	- Installing Python"
darling shell <<EOF
mkdir -p python_macos_x86_64
installer -pkg python-3.13.1-macos11.pkg -target / >> /dev/null 2>> /dev/null
cp -R /Library/Frameworks/Python.framework/Versions/3.13/* ./python_macos_x86_64/ >> /dev/null 2>> /dev/null
EOF

## Clean up temporary files
rm darling_0.1.20230310.jammy_amd64.deb
rm python-3.13.1-macos11.pkg

echo ">> Python 3.13.1 installation in Darling completed"
