# This file is part of pookie.

# Copyright (C) 2025 Andrés Lillo Ortiz

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

import subprocess

def wrapper(user_command, container_command):
    """
    Generate the command to create a wrapper for the specified command.
    This is used to ensure that the correct command is used in the Docker container.
    Place this command BEFORE the build command.

    Parameters:
    - container_command (str): The command to run inside the Docker container.
    - user_command (str): The command that the user specifies.

    Returns:
    - str: The command to create the wrapper.
    """
    return f'''mkdir -p /wrapper && echo -e "#!/bin/bash\n{container_command} "\\$@"" > /wrapper/{user_command} && chmod +x /wrapper/{user_command} && export PATH="/wrapper:$PATH" && '''

def rename_dist(original_dist_target, new_dist_target):
    """
    Generate the command to rename the built library files.
    Place this command AFTER the build command.

    Parameters:
    - original_target (str): The original target architecture.
    - new_target (str): The new target architecture.

    Returns:
    - str: The command to rename the built library files.
    """
    return f''' && for f in dist/*-{original_dist_target}.whl; do mv "$f" "${{f/{original_dist_target}/{new_dist_target}}}"; done'''

def install_dist(cp_version, dist_target):
    """
    Generate the command to install the built library.
    Place this command BEFORE the test command.

    Parameters:
    - cp_version (str): The CP version to use in the filename.
    - target (str): The target architecture.

    Returns:
    - str: The command to install the built library.
    """
    return f'''python3 -m pip install dist/*-cp{cp_version}-cp{cp_version}*-{dist_target}.whl >> /dev/null 2>> /dev/null && '''

def prepare_environment_macosx_11_0_x86_64(python_major_dot_minor_version):
    """
    Generate the command to prepare the environment for macOS builds.
    This includes setting up the compiler and linker flags.
    Place this command BEFORE the build command.

    Parameters:
    - python_major_dot_minor_version (str): The major and minor version of Python to use (e.g., "3.12").

    Returns:
    - str: The command to prepare the environment.
    """

    return f'''export LDSHARED='$(python3 -c "import sysconfig; print(sysconfig.get_config_var(\\"LDSHARED\\").replace(\\"--exclude-libs,ALL\\",\\"\"))")' && \
        export LDSHARED="$(pwd)/clang-wrapper.sh -shared" && \
        echo -e "#!/bin/bash\nexec o64-clang -fuse-ld=/osxcross/target/bin/x86_64-apple-darwin20.2-ld \"\\$@\"" > clang-wrapper.sh && chmod +x clang-wrapper.sh && \
        export CC=$(pwd)/clang-wrapper.sh && \
        export CXX=$CC && \
        export AR=x86_64-apple-darwin20.2-ar && \
        export RANLIB=x86_64-apple-darwin20.2-ranlib && \
        export STRIP=x86_64-apple-darwin20.2-strip && \
        export CFLAGS="--target=x86_64-apple-darwin -isysroot /osxcross/target/SDK/MacOSX11.1.sdk -I/python/include/python{python_major_dot_minor_version}" && \
        export LDFLAGS="-isysroot /osxcross/target/SDK/MacOSX11.1.sdk -Wl,-syslibroot,/osxcross/target/SDK/MacOSX11.1.sdk -L/python/lib -lpython{python_major_dot_minor_version}" \
        && '''

def prepare_environment_manylinux_2_17_x86_64_and_musllinux_1_2_x86_64(CC, CXX):
    """
    Generate the command to prepare the environment for manylinux and musllinux builds.
    Place this command BEFORE the build command.

    Parameters:
    - CC (str): The C compiler to use.
    - CXX (str): The C++ compiler to use.

    Returns:
    - str: The command to prepare the environment.
    """

    return f'''export CC={CC} && export CXX={CXX} && '''

def fix_EXT_SUFFIX(py_version_nodot, new_base_os, new_dist_target):
    """
    Generate the command to fix the EXT_SUFFIX for cross builds.
    This is necessary to ensure that the built library can be imported correctly.
    Place this command AFTER the build command.

    Parameters:
    - py_version_nodot (str): The CP version to use in the filename.
    - new_base_os (str): The new base OS for the library (target name in .so files).
    - new_dist_target (str): The new distribution target.

    Returns:
    - str: The command to fix the EXT_SUFFIX.
    """

    return f''' && cd dist && \
        orig_whl=$(ls *-cp{py_version_nodot}-cp{py_version_nodot}-linux_x86_64.whl) && \
        unzip -o *-cp{py_version_nodot}-cp{py_version_nodot}-linux_x86_64.whl -d tmp && cd tmp && \
        find . -type f -name "*.cpython-{py_version_nodot}-x86_64-linux-gnu.so" -exec bash -c 'mv "$0" "${{0/-x86_64-linux-gnu/-{new_base_os}}}"' {{}} \\; && \
        sed -i 's/linux_x86_64/{new_dist_target}/g' *.dist-info/WHEEL && \
        sed -i 's/x86_64-linux-gnu/{new_base_os}/g' *.dist-info/RECORD && \
        zip -r "../${{orig_whl/-linux_x86_64/-{new_dist_target}}}" * && \
        cd .. && rm -rf *-cp{py_version_nodot}-cp{py_version_nodot}-linux_x86_64.whl tmp/ ../clang-wrapper.sh'''

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
        for minor in python_versions_dic:

            py_version_nodot = '3' + minor
            python_major_dot_minor_version = '3.' + minor

            if target == 'manylinux_2_17_x86_64':

                image_name = f"manylinux-lvl3-cp{py_version_nodot}-manylinux_2_17"
                original_dist_target = "linux_x86_64"
                new_dist_target = "manylinux_2_17_x86_64.manylinux2014_x86_64"
                python_executable = '/python/bin/python3'
                pip_executable = '/python/bin/pip3'
                CC = "gcc"
                CXX = "g++"

                # build the library
                if build != None:

                    build_command = \
                        wrapper("python3", python_executable) + wrapper("pip3", pip_executable) + wrapper("python", python_executable) + wrapper("pip", pip_executable) + \
                        prepare_environment_manylinux_2_17_x86_64_and_musllinux_1_2_x86_64(CC, CXX) + \
                        build + \
                        rename_dist(original_dist_target, new_dist_target)

                    print(f">> Building the library for cp-{py_version_nodot}-{target}")
                    run_lvl3_image(image_name, build_command, host_workspace_path, logfile)

                # test the library
                if test != None:

                    test_command = \
                        wrapper("python3", python_executable) + wrapper("pip3", pip_executable) + wrapper("python", python_executable) + wrapper("pip", pip_executable) + \
                        install_dist(py_version_nodot, new_dist_target) + \
                        test

                    print(f">> Testing the library for cp-{py_version_nodot}-{target}")
                    run_lvl3_image(image_name, test_command, host_workspace_path, None)

            if target == 'musllinux_1_2_x86_64':

                image_name = f"musllinux-lvl3-cp{py_version_nodot}-musllinux_1_2"
                original_dist_target = "linux_x86_64"
                new_dist_target = "musllinux_1_2_x86_64"
                python_executable = '/python/bin/python3'
                pip_executable = '/python/bin/pip3'
                CC = "gcc"
                CXX = "g++"

                # build the library
                if build != None:

                    build_command = \
                        wrapper("python3", python_executable) + wrapper("pip3", pip_executable) + wrapper("python", python_executable) + wrapper("pip", pip_executable) + \
                        prepare_environment_manylinux_2_17_x86_64_and_musllinux_1_2_x86_64(CC, CXX) + \
                        build + \
                        rename_dist(original_dist_target, new_dist_target)

                    print(f">> Building the library for cp-{py_version_nodot}-{target}")
                    run_lvl3_image(image_name, build_command, host_workspace_path, logfile)

                # test the library
                if test != None:

                    test_command = \
                        wrapper("python3", python_executable) + wrapper("pip3", pip_executable) + wrapper("python", python_executable) + wrapper("pip", pip_executable) + \
                        install_dist(py_version_nodot, new_dist_target) + \
                        test

                    print(f">> Testing the library for cp-{py_version_nodot}-{target}")
                    run_lvl3_image(image_name, test_command, host_workspace_path, None)

            if target == 'win_amd64':

                image_name = f"win-macosx-pookie-lvl3-cp{py_version_nodot}-win"
                python_executable = 'wine /python/python.exe'
                pip_executable = 'wine /python/python.exe -m pip'

                # build the library
                if build != None:

                    build_command = \
                        wrapper("python3", python_executable) + wrapper("pip3", pip_executable) + wrapper("python", python_executable) + wrapper("pip", pip_executable) + \
                        build

                    print(f">> Building the library for cp-{py_version_nodot}-{target}")
                    run_lvl3_image(image_name, build_command, host_workspace_path, logfile)

            if target == 'macosx_11_0_x86_64':

                image_name = f"win-macosx-pookie-lvl3-cp{py_version_nodot}-macosx"
                new_base_os = "darwin"
                new_dist_target = "macosx_11_0_x86_64"
                python_executable = '/python_cross/bin/python3'
                pip_executable = '/python_cross/bin/pip3'

                # build the library
                if build != None:

                    build_command = \
                        wrapper("python3", python_executable) + wrapper("pip3", pip_executable) + wrapper("python", python_executable) + wrapper("pip", pip_executable) + \
                        prepare_environment_macosx_11_0_x86_64(python_major_dot_minor_version) + \
                        build + \
                        fix_EXT_SUFFIX(py_version_nodot, new_base_os, new_dist_target)

                    print(f">> Building the library for cp-{py_version_nodot}-{target}")
                    run_lvl3_image(image_name, build_command, host_workspace_path, logfile)

                # test the library
                if test != None:

                    print(f">> Testing the library for cp-{py_version_nodot}-{target}")
                    print("Not supported yet :(")