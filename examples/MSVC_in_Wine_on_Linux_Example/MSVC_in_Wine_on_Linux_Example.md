# Example of Setting Up and Running MSVC in Wine on Linux

## Install dependencies
```bash
sudo apt-get update
sudo apt-get install -y wine64 python3 msitools ca-certificates winbind
```

## Clone the repository
```bash
git clone https://github.com/mstorsjo/msvc-wine.git
```

## Download and Unpack MSVC
```bash
./msvc-wine/vsdownload.py --dest ./msvc
```

## Install MSVC
```bash
./msvc-wine/install.sh ./msvc
```
