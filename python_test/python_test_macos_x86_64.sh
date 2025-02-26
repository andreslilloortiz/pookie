#!/bin/bash

# Test Python 3.13.1 for MacOS x86_64
echo ">> Test Python 3.13.1 for MacOS x86_64"

## Download Darling
echo "	- Downloading Darling"
wget https://github.com/darlinghq/darling/releases/download/v0.1.20230310_update_sources_11_5/darling_0.1.20230310.jammy_amd64.deb >> /dev/null 2>> /dev/null

## Install Darling
echo "	- Installing Darling"
sudo dpkg -i darling_0.1.20230310.jammy_amd64.deb >> /dev/null 2>> /dev/null

## Remove unnecessary files
rm darling_0.1.20230310.jammy_amd64.deb