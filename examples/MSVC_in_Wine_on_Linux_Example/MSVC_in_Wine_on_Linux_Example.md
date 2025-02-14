# Example of Setting Up and Running MSVC in Wine on Linux

A **CMakeLists.txt** file is required.

## Install dependencies
```bash
sudo apt-get update
sudo apt-get install -y wine64 python3 msitools ca-certificates winbind
```

## Clone the repository
```bash
git clone https://github.com/mstorsjo/msvc-wine.git
cd msvc-wine
```

## Download and Unpack MSVC
```bash
./vsdownload.py --dest ../my_msvc/opt/msvc
```

## Install MSVC
```bash
./install.sh ../my_msvc/opt/msvc
```

## Add the MSVC installation to the path
```bash
cd ..
export PATH=$(realpath ./my_msvc/opt/msvc/bin/x64):$PATH
```

## Run CMake command with a few extra settings
```bash
mkdir build
cd build
CC=cl CXX=cl cmake .. -DCMAKE_BUILD_TYPE=Release -DCMAKE_SYSTEM_NAME=Windows
make
```

## Run the executable exe
```bash
wine cprogram.exe
```
