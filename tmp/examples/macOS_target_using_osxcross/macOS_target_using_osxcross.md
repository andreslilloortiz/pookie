# Download a packaged SDK
```bash
wget https://github.com/joseluisq/macosx-sdks/releases/download/11.1/MacOSX11.1.sdk.tar.xz
```

# Download osxcross
```bash
git clone https://github.com/tpoechtrager/osxcross.git
```

# Move your packaged SDK to the tarballs/ directory
```bash
mv MacOSX11.1.sdk.tar.xz osxcross/tarballs/
```

# Dependencies
```bash
cd osxcross
sudo tools/get_dependencies.sh
```

# Building OSXCross
```bash
./build.sh
```

# Add the compiler to the path
```bash
export PATH=$PATH:/home/andres/Documentos/TFG/pookie/examples/macOS_target_using_osxcross/osxcross/target/bin
```

# Compile the c program
```bash
o64-clang++ cprogram.c -O3 -o cprogram
```

# Run with Darling
```bash
darling shell
./cprogram
```

# Compile the python package for x86_64
```bash
o64-clang -shared -o sum.so -undefined dynamic_lookup -I/home/andres/Documentos/TFG/pookie/python_compile/python-3.13-x86_64-macos/include/python3.13 sum.c
```

# Compile the python package for arm64
```bash
oa64-clang -shared -o sum.so -undefined dynamic_lookup -I/home/andres/Documentos/TFG/pookie/python_compile/python-3.13-x86_64-macos/include/python3.13 sum.c
```

# Compile the python package for arm64e
```bash
oa64e-clang -shared -o sum.so -undefined dynamic_lookup -I/home/andres/Documentos/TFG/pookie/python_compile/python-3.13-x86_64-macos/include/python3.13 sum.c
```
