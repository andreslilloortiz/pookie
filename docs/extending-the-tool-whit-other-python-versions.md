# Extending the Tool with Other Python Versions

By following these steps, you can extend the tool to support additional Python versions across multiple targets.

## Updating `pookie.py`

Before modifying the Dockerfile of each desired target, you need to update the main `pookie.py` file:

- Locate the section where the command-line options are defined using `argparse`. This section is in the first lines of the `main` function.

- In the `--python-version` option, add the new Python version to both the `choices` list and the `default` value if needed.

## Linux x86_64

For Linux x86_64, you need to modify the `Dockerfile.x86_64-linux` file located in the `images` folder.

- Navigate to the `# Download and install the Python versions` section.

- Add the new Python version using a similar approach to the existing ones.

- Generally, the same code can be used, just replacing the Python version in the necessary commands.

- Python versions are installed directly inside the Docker image.

## Windows x86_64

For Windows x86_64, the process is slightly different:

- Follow the guide in [`cross-install-python-x86_64-windows.md`](cross-install-python-x86_64-windows.md) found in the `docs` folder to manually install the desired Python version on your local machine.

- Once installed, modify the `Dockerfile.all-windows` file in the `images` folder.

- Locate the `# Add the python installation` section.

- Add the new Python version using the same command structure as the existing ones, replacing the Python version accordingly.

## macOS x86_64

The process for macOS x86_64 follows the same approach as Windows x86_64:

- Follow the guide in [`cross-install-python-x86_64-macos.md`](cross-install-python-x86_64-macos.md) found in the `docs` folder to manually install the desired Python version on your local machine.

- Modify the `Dockerfile.all-macos` file in the `images` folder.

- Locate the `# Add the python installation` section.

- Add the new Python version using the same command structure as the existing ones, replacing the Python version accordingly.
