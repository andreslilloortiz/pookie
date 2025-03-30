# Compiling a Python Package for Windows using Wine

## Requirements
To compile a Python package for Windows using Wine, you will need:
- **Microsoft Visual C++ (MSVC)**: Required for compiling the C code.
- **Python for Windows**: Needed to run the compiled module inside Wine.
- **Wine**: Allows running Windows programs (like MSVC and Python) on Linux.

## Define paths for the compiler, includes, libraries, and Python executable
```bash
CL_PATH="/home/andres/Documentos/TFG/pookie/examples/MSVC_in_Wine_on_Linux_Example/my_msvc/opt/msvc/bin/x64/cl.exe"
INCLUDE_PATH="/home/andres/Documentos/TFG/pookie/python_compile/python-3.13-x86_64-windows/include"
LIB_PATH="/home/andres/Documentos/TFG/pookie/python_compile/python-3.13-x86_64-windows/libs"
PYTHON_PATH="/home/andres/Documentos/TFG/pookie/python_compile/python-3.13-x86_64-windows/python.exe"
```

## Compile sum.c using MSVC inside Wine
```bash
wine "$CL_PATH" /LD /I"$INCLUDE_PATH" sum.c /link /LIBPATH:"$LIB_PATH" /OUT:sum.pyd
```

## Compile sum.c using setuptools inside Wine

### Get pip
```bash
wget https://bootstrap.pypa.io/get-pip.py
wine $PYTHON_PATH get-pip.py
```

### Install setuptools and wheel
```bash
wine $PYTHON_PATH -m pip install setuptools wheel build
```

### Build the package
```bash
# this fails because it does not detect that the compiler has been changed and the error that MSVC is missing appears
wine $PYTHON_PATH -m build
```

### Install the generated package
```bash
# python3 -m pip install dist/sum-1.0-cp313-cp313-linux_x86_64.whl
```

## Run Python inside Wine to test the compiled module
```bash
wine $PYTHON_PATH
```

```python
>>> import sum
>>> sum.add(5, 2)
7
>>> quit()
```

## Screenshot of the Example
![Example in a terminal](Windows_Compile_Example.png)
