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

def build_lvl1_or_lvl2_image(tree, image_name, logfile):
    """
    Build a level 1 or level 2 Docker image.

    Parameters:
    - tree (str): The tree from the Docker layer graph.
    - image_name (str): The specific image name to build.
    - logfile (file object): File object to log the output of the build process.
    """
    if not image_exists(image_name):
        subprocess.run([
            'docker',
                'build',
                '-f',
                    f'/images/{tree}/Dockerfile.{image_name}',
                '-t',
                    image_name,
                '.'
        ], stdout=logfile, stderr=logfile)

def build_lvl3_image(tree, general_image_name, image_name, python_url, logfile):
    """
    Build a level 3 CP3xx Docker image.

    Parameters:
    - tree (str): The tree from the Docker layer graph.
    - general_image_name (str): The image name.
    - image_name (str): The specific image name to build.
    - python_file (str): The Python file downloaded quith python_url.
    - python_url (str): The URL for the Python source.
    - logfile (file object): File object to log the output of the build process.
    """
    if not image_exists(image_name):
        subprocess.run([
            'docker',
                'build',
                '-f',
                    f'/images/{tree}/Dockerfile.{general_image_name}',
                '-t',
                    image_name,
                '--build-arg',
                    f'PYTHON_URL={python_url}',
                '.'
        ], stdout=logfile, stderr=logfile)

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
            print(f">> Creating docker images for {target}")
            tree = "manylinux"

            # level 1
            image_name = "manylinux-lvl1-base"
            build_lvl1_or_lvl2_image(tree, image_name, logfile)

            # level 2
            image_name = "manylinux-lvl2-gnu-gcc"
            build_lvl1_or_lvl2_image(tree, image_name, logfile)

            # level 3
            for minor, target_data in python_versions_dic.items():

                general_image_name = "manylinux-lvl3-cp3xx-manylinux_2_17"

                py_version_nodot = '3' + minor
                image_name = f"manylinux-lvl3-cp{py_version_nodot}-manylinux_2_17"

                python_file = target_data[target]["filename"]
                python_url = target_data[target]["url"]

                build_lvl3_image(tree, general_image_name, image_name, python_url, logfile)

        if target == 'musllinux_1_2_x86_64':
            print(f">> Creating docker images for {target}")
            tree = "musllinux"

            # level 1
            image_name = "musllinux-lvl1-base"
            build_lvl1_or_lvl2_image(tree, image_name, logfile)

            # level 2
            image_name = "musllinux-lvl2-musl-gcc"
            build_lvl1_or_lvl2_image(tree, image_name, logfile)

            # level 3
            for minor, target_data in python_versions_dic.items():

                general_image_name = "musllinux-lvl3-cp3xx-musllinux_1_2"

                py_version_nodot = '3' + minor
                image_name = f"musllinux-lvl3-cp{py_version_nodot}-musllinux_1_2"

                python_file = target_data[target]["filename"]
                python_url = target_data[target]["url"]

                build_lvl3_image(tree, general_image_name, image_name, python_url, logfile)

        if target == 'win_amd64':
            print(">> Creating docker images for win_amd64")
            tree = "win-macosx-pookie"

            # level 1
            # (same base level as pookie so its created)

            # level 2
            image_name = "win-macosx-pookie-lvl2-msvc-mingw64"
            build_lvl1_or_lvl2_image(tree, image_name, logfile)

            # level 3
            for python_version, urls_dic in python_versions_dic.items():

                general_image_name = "win-macosx-pookie-lvl3-cp3xx-win"

                cp_version_parts = python_version.split(".")
                cp_version = f"{cp_version_parts[0]}{cp_version_parts[1]}"
                image_name = f"win-macosx-pookie-lvl3-cp{cp_version}-win"

                python_url = urls_dic["exe"]

                build_lvl3_image(tree, general_image_name, image_name, python_version, python_url, logfile)

        if target == 'macosx_11_0_x86_64':
            print(">> Creating docker images for macosx_11_0_x86_64")
            tree = "win-macosx-pookie"

            # level 1
            # (same base level as pookie so its created)

            # level 2
            image_name = "win-macosx-pookie-lvl2-osxcross"
            build_lvl1_or_lvl2_image(tree, image_name, logfile)

            # level 3
            for python_version, urls_dic in python_versions_dic.items():

                general_image_name = "win-macosx-pookie-lvl3-cp3xx-macosx"

                cp_version_parts = python_version.split(".")
                cp_version = f"{cp_version_parts[0]}{cp_version_parts[1]}"
                image_name = f"win-macosx-pookie-lvl3-cp{cp_version}-macosx"

                python_url = urls_dic["pkg"]

                build_lvl3_image(tree, general_image_name, image_name, python_version, python_url, logfile)