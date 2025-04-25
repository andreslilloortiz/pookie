import subprocess

def image_exists(image_name):
    """
    Checks if a Docker image already exists.

    Parameters:
    - image_name (str): The name of the Docker image to check.

    Returns:
    - bool: True if the image exists, False otherwise.
    """
    result = subprocess.run([
        'docker',
            'images',
            '-q',
                image_name],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    return bool(result.stdout.strip())

def build_docker_images(targets, logfile, python_versions_dic):
    """
    Build Docker images for the specified targets.

    Parameters:
    - targets (list): List of target architectures to build images for.
    - logfile (file object): File object to log the output of the build process.
    - python_versions_dic (dict): Dictionary containing Python versions and their URLs.
    """
    for target in targets:

        if target == 'manylinux_2_17_x86_64':
            print(">> Creating docker images for manylinux_2_17_x86_64")

            # level 0
            if not image_exists("ubuntu-1804"):
                subprocess.run([
                    'docker',
                        'build',
                        '-f',
                            '/images/level 0/Dockerfile.ubuntu-1804',
                        '-t',
                            'ubuntu-1804',
                        '.'
                ], stdout=logfile, stderr=logfile)

            # level 1
            if not image_exists("gnu-gcc"):
                subprocess.run([
                    'docker',
                        'build',
                        '-f',
                            '/images/level 1/Dockerfile.gnu-gcc',
                        '-t',
                            'gnu-gcc',
                        '.'
                ], stdout=logfile, stderr=logfile)

            # level 2
            for python_version, urls_dic in python_versions_dic.items():

                cp_version_parts = python_version.split(".")
                cp_version = f"{cp_version_parts[0]}{cp_version_parts[1]}"

                if not image_exists(f"cp{cp_version}-manylinux_2_17_x86_64"):
                    subprocess.run([
                        'docker',
                            'build',
                            '-f',
                                '/images/level 2/Dockerfile.cp3xx-manylinux_2_17_x86_64',
                            '-t',
                                f'cp{cp_version}-manylinux_2_17_x86_64',
                            '--build-arg',
                                f'PYTHON_VERSION={python_version}',
                            '--build-arg',
                                f'PYTHON_URL={urls_dic["tar_xz"]}',
                            '.'
                    ], stdout=logfile, stderr=logfile)