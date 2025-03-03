# Download a packaged SDK
```bash
wget https://github.com/joseluisq/macosx-sdks/releases/download/10.13/MacOSX10.13.sdk.tar.xz
```

# Download osxcross
```bash
git clone https://github.com/tpoechtrager/osxcross.git
```

# Move your packaged SDK to the tarballs/ directory
```bash
mv MacOSX10.13.sdk.tar.xz osxcross/tarballs/
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
export PATH=$PATH:/home/andres/Documentos/TFG/actionless/examples/macOS_target_using_osxcross/osxcross/target/bin
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

# Compile the python package
```bash
o64-clang -shared -o sum.so -undefined dynamic_lookup -I/home/andres/Documentos/TFG/actionless/python_compile/python_macos_x86_64/include/python3.13 sum.c
```
