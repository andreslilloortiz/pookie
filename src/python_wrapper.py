def wrapper_python3(new_python3_command):
    """
    Generate the command to create a wrapper for Python 3.
    This is used to ensure that the correct Python interpreter is used in the Docker container.
    Place this command BEFORE the build command.

    Parameters:
    - new_python3_command (str): The command to run the new Python 3 interpreter.

    Returns:
    - str: The command to create the wrapper.
    """
    return f'''mkdir -p /wrapper && echo -e "#!/bin/bash\n{new_python3_command} "\\$@"" > /wrapper/python3 && chmod +x /wrapper/python3 && export PATH="/wrapper:$PATH" && '''

def wrapper_python(new_python_command):
    """
    Generate the command to create a wrapper for Python.
    This is used to ensure that the correct Python interpreter is used in the Docker container.
    Place this command BEFORE the build command.

    Parameters:
    - new_python_command (str): The command to run the new Python interpreter.

    Returns:
    - str: The command to create the wrapper.
    """
    return f'''mkdir -p /wrapper && echo -e "#!/bin/bash\n{new_python_command} "\\$@"" > /wrapper/python && chmod +x /wrapper/python && export PATH="/wrapper:$PATH" && '''

def wrapper_pip3(new_pip3_command):
    """
    Generate the command to create a wrapper for pip3.
    This is used to ensure that the correct pip interpreter is used in the Docker container.
    Place this command BEFORE the build command.

    Parameters:
    - new_pip3_command (str): The command to run the new pip3 interpreter.

    Returns:
    - str: The command to create the wrapper.
    """
    return f'''mkdir -p /wrapper && echo -e "#!/bin/bash\n{new_pip3_command} "\\$@"" > /wrapper/pip3 && chmod +x /wrapper/pip3 && export PATH="/wrapper:$PATH" && '''

def wrapper_pip(new_pip_command):
    """
    Generate the command to create a wrapper for pip.
    This is used to ensure that the correct pip interpreter is used in the Docker container.
    Place this command BEFORE the build command.

    Parameters:
    - new_pip_command (str): The command to run the new pip interpreter.

    Returns:
    - str: The command to create the wrapper.
    """
    return f'''mkdir -p /wrapper && echo -e "#!/bin/bash\n{new_pip_command} "\\$@"" > /wrapper/pip && chmod +x /wrapper/pip && export PATH="/wrapper:$PATH" && '''