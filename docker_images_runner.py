import subprocess
import os

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

                # build the library
                if build != None:

                    build_command = build + ' && for f in dist/*-linux_x86_64.whl; do mv "$f" "${f/linux_x86_64/manylinux_2_17_x86_64.manylinux2014_x86_64}"; done'

                    print(f">> Building the library for cp-{cp_version}-{target}")
                    run_lvl3_image(image_name, build_command, host_workspace_path, logfile)

                # test the library
                if test != None:

                    test_command = f"python3 -m pip install dist/*-cp{cp_version}-cp{cp_version}-manylinux_2_17_x86_64.manylinux2014_x86_64.whl >> /dev/null 2>> /dev/null && " + test

                    print(f">> Testing the library for cp-{cp_version}-{target}")
                    run_lvl3_image(image_name, test_command, host_workspace_path, None)

    # Delete __pycache__
    subprocess.run([
        'rm',
            '-rf',
            '__pycache__'
    ], stdout = logfile, stderr = logfile)