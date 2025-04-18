# pookie

Tool for Automating the Build and Testing Process of Native Python Libraries Using Cross-Compilation and Emulation Technologies.

## About the Project

This project focuses on developing an Open Source application to optimize the building and testing of Python libraries that include low-level code in C and C++. These libraries, crucial for data-intensive tasks, require specific compilation processes to ensure performance and portability across different operating systems and architectures.

The proposed solution leverages technologies like QEMU and Wine to implement cross-compilation and emulation, enabling efficient binary generation without the time and resource limitations of commercial continuous integration platforms. This project aims to enhance accessibility and efficiency in the development of scientific and computational software.

## Quick Start

1. **Add source and test files**

    Place the files you want to compile and test inside the `workspace` directory.

2. **Clone Python prebuilt binaries**

    This repository contains precompiled Python binaries for multiple platforms and architectures (targets), organized by operating system and CPU architecture.

    Clone this repository in the root of pookie.

    ```bash
    git clone https://github.com/andreslilloortiz/python-prebuilt-binaries.git
    ```
3. **Build pookie Docker image**

    ```bash
    docker build -t pookie .
    ```

4. **Run pookie**

    ```bash
    docker run -it --rm \
        -v $(pwd)/workspace:/workspace \
        -e WORKSPACE_PWD=$(pwd)/workspace \
        -w /workspace \
        -v /var/run/docker.sock:/var/run/docker.sock \
        pookie --help
    ```
## Running Pookie: Command Line Options

> **Recomendation:** First run Pookie without arguments to allow it to generate the required Docker images for building and testing. This may take a few minutes the first time.

| Argument                                                                                               | Description                                                                  |
|--------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------|
| `-h, --help`                                                                                           | Show this help message and exit                                              |
| `--build BUILD [BUILD ...]`                                                                            | Python library source file(s) to build                                       |
| `--test TEST [TEST ...]`                                                                               | Test Python file(s) to run after building the library                        |
| `--python-version {3.13.2,3.12.9,3.11.9,3.10.11} [{3.13.2,3.12.9,3.11.9,3.10.11} ...]`                 | Python version(s) to compile for (if not specified: all)                     |
| `--target {x86_64-linux,x86_64-windows,x86_64-macos} [{x86_64-linux,x86_64-windows,x86_64-macos} ...]` | Target platform(s) to build and test the library for (if not specified: all) |
| `--clean`                                                                                              | Clean the workspace by removing all files and directories                    |

> **Note:** For `x86_64-linux` target, compilation uses setuptools. That means you can provide via `--build` a `setup.py` file, which defines the necessary source files.

## Example

Compile the source file `mylib.c` and test it with `test_mylib.py` for Python version `3.12.9` targeting both `x86_64-linux` and `x86_64-windows`.

```bash
docker run -it --rm \
    -v $(pwd)/workspace:/workspace \
    -e WORKSPACE_PWD=$(pwd)/workspace \
    -w /workspace \
    -v /var/run/docker.sock:/var/run/docker.sock \
    pookie \
    --build mylib.c \
    --test test_mylib.py \
    --python-version 3.12.9 \
    --target x86_64-linux x86_64-windows
```

## Output

Build artifacts (e.g., .so, .pyd, .whl) will be placed inside versioned folders in the workspace directory, such as:

```bash
workspace
    ├── 3.10.11-x86_64-linux
    ├── 3.10.11-x86_64-macos
    ├── 3.10.11-x86_64-windows
    ├── 3.11.9-x86_64-linux
    ├── 3.11.9-x86_64-macos
    ├── 3.11.9-x86_64-windows
    ├── 3.12.9-x86_64-linux
    ├── 3.12.9-x86_64-macos
    ├── 3.12.9-x86_64-windows
    ├── 3.13.2-x86_64-linux
    ├── 3.13.2-x86_64-macos
    ├── 3.13.2-x86_64-windows
```

## Extending the Tool with Other Python Versions

By following the steps in [`extending-the-tool-whit-other-python-versions.md`](docs/extending-the-tool-whit-other-python-versions.md) found in the `docs` folder, you can extend the tool to support additional Python versions across multiple targets.

---

I hope this guide has been helpful!