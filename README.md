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

3. **Build pookie-base Docker image**

    ```bash
    docker build -t pookie-base -f images/Dockerfile.pookie-base .
    ```

4. 3. **Build pookie-launcher Docker image**

    ```bash
    docker build -t pookie-launcher -f images/Dockerfile.pookie-launcher .
    ```

5. **Run pookie**

    You can run pookie either by using the Docker command directly or by executing a simple shell script.

    **Option 1**: Using Docker command directly.

    ```bash
    docker run -it --rm \
        -v $(pwd)/workspace:/workspace \
        -e WORKSPACE_PWD=$(pwd)/workspace \
        -w /workspace \
        -v /var/run/docker.sock:/var/run/docker.sock \
        pookie-launcher --help
    ```

    **Option 2**: Using the provided shell script.

    Make the script executable.

    ```bash
    chmod +x pookie.sh
    ```

    Run the script.

    ```bash
    ./pookie.sh --help
    ```


## Running Pookie: Command Line Options

> **Recomendation:** First run Pookie without arguments to allow it to generate the required Docker images for building and testing. This may take a few minutes the first time.

| Argument                                                                                               | Description                                                                  |
|--------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------|
| `-h, --help`                                                                                           | Show this help message and exit                                              |
| `--clean`                                                                                              | Clean the workspace by removing all files and directories                    |
| `--build BUILD [BUILD ...]`                                                                            | Python command to build                                                      |
| `--test TEST`                                                                                          | Test Python command to run after building the library                        |
| `--python-version {3.13.2,3.12.9,3.11.9,3.10.11} [{3.13.2,3.12.9,3.11.9,3.10.11} ...]`                 | Python version(s) to compile for (if not specified: all)                     |
| `--target {x86_64-linux,x86_64-windows,x86_64-macos} [{x86_64-linux,x86_64-windows,x86_64-macos} ...]` | Target platform(s) to build and test the library for (if not specified: all) |

> **Note:** For `x86_64-linux` target, compilation uses setuptools. That means you can provide via `--build` a `setup.py` file, which defines the necessary source files.

## Examples

Compile the source file `mylib.c` and test it with `test.py` script for Python versions `3.12.9` and `3.11.9` targeting both `x86_64-macos` and `x86_64-windows`.

```bash
./pookie.sh \
    --build mylib.c \
    --test "python3 test.py" \
    --python-version 3.12.9 3.11.9 \
    --target x86_64-macos x86_64-windows
```

Compile the source files with `setup.py` file and test it with test files in the module `tests` (directory with `__init__.py`) for Python version `3.10.11` targeting `x86_64-linux`.

```bash
./pookie.sh \
    --build setup.py \
    --test "python3 -m tests" \
    --python-version 3.10.11 \
    --target x86_64-linux
```

Compile the source files with `setup.py` file and test it with test files located in the `tests` folder using `pytest` for Python versions `3.13.2` and `3.12.9` targeting `x86_64-linux`.

```bash
./pookie.sh \
    --build setup.py \
    --test "python3 -m pip install pytest && pytest tests/test1.py && pytest tests/test2.py" \
    --python-version 3.13.2 3.12.9 \
    --target x86_64-linux
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

## Developer Notes

During development, if you're rebuilding images frequently (for example, when testing changes) Docker may retain old layers from previous builds. Even when images are overwritten, the old layers can remain in the cache and gradually consume a large amount of disk space.

To check current Docker disk usage:

```bash
docker system df
```

To safely clean up dangling images and unused build cache:

```bash
docker image prune

docker builder prune
```

This will only remove dangling images (those that are untagged and not referenced by any container) and build cache not currently used by any active images or containers, helping to free up disk space without affecting running or tagged images.

---

I hope this guide has been helpful!