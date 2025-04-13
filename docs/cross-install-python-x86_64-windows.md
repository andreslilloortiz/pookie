# Guide to Installing Python 3.13.2 on Windows x86_64 using Wine

This document describes the steps required to compile and install Python 3.13.2 on a Windows x86_64 environment using Wine on a Linux system.

If you want to install a different version of Python, the steps are generally the same, but you will need to change the version number in the relevant commands.

In the `scripts` folder, there is a script named `cross-install-python-x86_64-windows.sh` that executes the commands outlined in this guide.

> **IMPORTANT:** These commands are designed to be run from the `scripts` folder.

More information:

[1] "WineHQ - Run Windows applications on Linux, BSD, Solaris, and macOS," WineHQ. Accessed: December 1, 2024. [Online]. Available at: https://www.winehq.org/

## Prerequisites

- A Debian/Ubuntu-based Linux system.
- Superuser permissions (sudo).
- Internet connection to download packages and dependencies.

## Installation Steps

### 1. Install Wine

Wine is required to run Windows installers on Linux.

#### Enable 32-bit architecture

```bash
sudo dpkg --add-architecture i386
```

#### Add repository key

```bash
sudo mkdir -pm755 /etc/apt/keyrings

wget -O - https://dl.winehq.org/wine-builds/winehq.key | sudo gpg --dearmor -o /etc/apt/keyrings/winehq-archive.key -
```

#### Add Wine repository

```bash
sudo wget -NP /etc/apt/sources.list.d/ https://dl.winehq.org/wine-builds/ubuntu/dists/jammy/winehq-jammy.sources

sudo apt update
```

#### Install Wine

```bash
sudo apt install --install-recommends winehq-stable

winecfg
```

### 2. Download Python 3.13.2

```bash
wget https://www.python.org/ftp/python/3.13.2/python-3.13.2-amd64.exe
```

### 3. Install Python using Wine

```bash
mkdir -p ../python-prebuilt-binaries/python-3.13.2-x86_64-windows

wine python-3.13.2-amd64.exe /quiet InstallAllUsers=1 TargetDir="%CD%\..\..\python-prebuilt-binaries\python-3.13.2-x86_64-windows" PrependPath=1
```

### 4. Clean up unnecessary files

```bash
rm python-3.13.2-amd64.exe
```

## Test the Installation

To verify that Python has been installed correctly, run the following command:

```bash
wine ../python-prebuilt-binaries/python-3.13.2-x86_64-windows/python.exe --version
```

This should output the installed Python version.

---

I hope this guide has been helpful!