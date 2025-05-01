import subprocess
import os

def rename_dist(original_dist_target, new_dist_target):
    """
    Generate the command to rename the built library files.
    Place this command after the build command.

    Parameters:
    - original_target (str): The original target architecture.
    - new_target (str): The new target architecture.

    Returns:
    - str: The command to rename the built library files.
    """
    return f' && for f in dist/*-{original_dist_target}.whl; do mv "$f" "${{f/{original_dist_target}/{new_dist_target}}}"; done'

def install_dist(cp_version, dist_target):
    """
    Generate the command to install the built library.
    Place this command before the test command.

    Parameters:
    - cp_version (str): The CP version to use in the filename.
    - target (str): The target architecture.

    Returns:
    - str: The command to install the built library.
    """
    return f"python3 -m pip install dist/*-cp{cp_version}-cp{cp_version}*-{dist_target}.whl >> /dev/null 2>> /dev/null && "

def wrapper_python3(new_python3_command):
    """
    Generate the command to create a wrapper for Python 3.
    This is used to ensure that the correct Python interpreter is used in the Docker container.
    Place this command before the build command.

    Parameters:
    - new_python3_command (str): The command to run the new Python 3 interpreter.

    Returns:
    - str: The command to create the wrapper.
    """
    return f'echo -e "#!/bin/bash\n{new_python3_command} \"\$@\"" > /bin/python3 && chmod +x /bin/python3 && '

def run_lvl3_image(image_name, command, host_workspace_path, logfile):
    """
    Run a level 3 CP3xx Docker image.

    Parameters:
    - image_name (str): The specific image name to run.
    - command (str): The command to run inside the Docker container.
    - host_workspace_path (str): The path to the host workspace.
    - logfile (file object): File object to log the output of the run process.
    """
    subprocess.run([
        'docker',
            'run',
            '-it',
            '--rm',
            '-v',
                f'{host_workspace_path}:/workspace',
            '-w',
                f'/workspace',
            image_name,
            '/bin/bash',
                '-c',
                command
    ], stdout = logfile, stderr = logfile)

def run_docker_images(targets, logfile, python_versions_dic, build, test, host_workspace_path):
    """
    Run Docker images for building and testing the library.

    Parameters:
    - targets (list): List of target architectures.
    - logfile (file object): File object to log the output of the run process.
    - python_versions_dic (dict): Dictionary of Python versions.
    - build (str): Command to build the library.
    - test (str): Command to test the library.
    - host_workspace_path (str): Path to the host workspace.
    """

    # Run build and test commands
    for target in targets:
        for python_version in python_versions_dic:

            cp_version_parts = python_version.split(".")
            cp_version = f"{cp_version_parts[0]}{cp_version_parts[1]}"

            # manylinux_2_17_x86_64
            if target == 'manylinux_2_17_x86_64':

                image_name = f"manylinux-lvl3-cp{cp_version}-manylinux_2_17"
                original_dist_target = "linux_x86_64"
                new_dist_target = "manylinux_2_17_x86_64.manylinux2014_x86_64"

                # build the library
                if build != None:

                    build_command = build + rename_dist(original_dist_target, new_dist_target)

                    print(f">> Building the library for cp-{cp_version}-{target}")
                    run_lvl3_image(image_name, build_command, host_workspace_path, logfile)

                # test the library
                if test != None:

                    test_command = install_dist(cp_version, new_dist_target) + test

                    print(f">> Testing the library for cp-{cp_version}-{target}")
                    run_lvl3_image(image_name, test_command, host_workspace_path, None)

            # musllinux_1_2_x86_64
            if target == 'musllinux_1_2_x86_64':

                image_name = f"musllinux-lvl3-cp{cp_version}-musllinux_1_2"
                original_dist_target = "linux_x86_64"
                new_dist_target = "musllinux_1_2_x86_64"

                # build the library
                if build != None:

                    build_command = build + rename_dist(original_dist_target, new_dist_target)

                    print(f">> Building the library for cp-{cp_version}-{target}")
                    run_lvl3_image(image_name, build_command, host_workspace_path, logfile)

                # test the library
                if test != None:

                    test_command = install_dist(cp_version, new_dist_target) + test

                    print(f">> Testing the library for cp-{cp_version}-{target}")
                    run_lvl3_image(image_name, test_command, host_workspace_path, None)

            # win_amd64
            if target == 'win_amd64':

                image_name = f"win-macosx-pookie-lvl3-cp{cp_version}-win"
                new_python3_command = f"wine /python-{python_version}-embed-amd64/python.exe"

                # build the library
                if build != None:

                    build_command = wrapper_python3(new_python3_command) + build

                    print(f">> Building the library for cp-{cp_version}-{target}")
                    run_lvl3_image(image_name, build_command, host_workspace_path, logfile)