#!/bin/bash

# Create Virtual Machine whit Qemu for Linux ARM64
echo ">> Create Virtual Machine whit Qemu for Linux ARM64"

## Install Qemu
sudo apt update >> /dev/null 2>> /dev/null
sudo apt install qemu-system-arm >> /dev/null 2>> /dev/null

## Download Linux ARM64 image
mkdir qemu-linux-arm64
cd qemu-linux-arm64
echo "	- Downloading image"
wget https://cloud-images.ubuntu.com/jammy/current/jammy-server-cloudimg-arm64.img >> /dev/null 2>> /dev/null

## Create necessary support files
echo "	- Creating necessary support files"
truncate -s 64m varstore.img
truncate -s 64m efi.img
dd if=/usr/share/qemu-efi-aarch64/QEMU_EFI.fd of=efi.img conv=notrunc >> /dev/null 2>> /dev/null

## Run an emulated ARM64 VM on x86
echo "	- Running an emulated ARM64 VM on x86"
sudo qemu-system-aarch64 \
 -m 2048 \
 -cpu max \
 -M virt \
 -drive if=pflash,format=raw,file=efi.img,readonly=on \
 -drive if=pflash,format=raw,file=varstore.img \
 -drive if=none,file=jammy-server-cloudimg-arm64.img,id=hd0 \
 -device virtio-blk-device,drive=hd0 \
 -netdev type=tap,id=net0 \
 -device virtio-net-device,netdev=net0
# -nographic \
