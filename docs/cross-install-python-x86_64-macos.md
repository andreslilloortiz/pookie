# Guide to Installing Python 3.13.2 on MacOS x86_64 using Darling

This document describes the steps required to compile and install Python 3.13.2 on a MacOS x86_64 environment using Darling on a Linux system.

If you want to install a different version of Python, the steps are generally the same, but you will need to change the version number in the relevant commands.

In the `scripts` folder, there is a script named `cross-install-python-x86_64-macos.sh` that executes the commands outlined in this guide.

**IMPORTANT:** These commands are designed to be run from the `scripts` folder.

More information:

[1] "Darling |." Accessed: December 1, 2024. [Online]. Available at: https://www.darlinghq.org/

## Prerequisites

- A Debian/Ubuntu-based Linux system.
- Superuser permissions (sudo).
- Internet connection to download packages and dependencies.

## Installation Steps

### 1. Install Darling

Darling is required to run macOS applications on Linux.

#### Download Darling

```bash
wget https://github.com/darlinghq/darling/releases/download/v0.1.20230310_update_sources_11_5/darling_0.1.20230310.jammy_amd64.deb
```

#### Install Darling

```bash
sudo dpkg -i darling_0.1.20230310.jammy_amd64.deb
```

### 2. Download Python 3.13.2

```bash
wget https://www.python.org/ftp/python/3.13.2/python-3.13.2-macos11.pkg
```

### 3. Install Python using Darling

```bash
sudo darling shell <<EOF
xcode-select --install
mkdir -p ../python-prebuilt-binaries/python-3.13.2-x86_64-macos
installer -pkg python-3.13.2-macos11.pkg -target /
cp -R /Library/Frameworks/Python.framework/Versions/3.13/* ../python-prebuilt-binaries/python-3.13.2-x86_64-macos
EOF
```

### 4. Clean up unnecessary files

```bash
rm darling_0.1.20230310.jammy_amd64.deb

rm python-3.13.2-macos11.pkg
```

## Test the Installation

To verify that Python has been installed correctly, run the following command:

```bash
darling shell ../python-prebuilt-binaries/python-3.13.2-x86_64-macos/bin/python3 --version
```

This should output the installed Python version.

---

I hope this guide has been helpful!
