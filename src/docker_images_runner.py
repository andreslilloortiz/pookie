import subprocess
from python_wrapper import wrapper_python3, wrapper_python, wrapper_pip3, wrapper_pip

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

    return f'''echo -e "#!/bin/bash\nexec o64-clang -fuse-ld=/osxcross/target/bin/x86_64-apple-darwin20.2-ld \"\\$@\"" > clang-wrapper.sh && chmod +x clang-wrapper.sh && \
        python_version=$(python3 --version | awk '{{print $2}}') && \
        export CC=$(pwd)/clang-wrapper.sh && \
        export CXX=$CC && \
        export AR=x86_64-apple-darwin20.2-ar && \
        export RANLIB=x86_64-apple-darwin20.2-ranlib && \
        export STRIP=x86_64-apple-darwin20.2-strip && \
        export PYTHON_ROOT="/python-${{python_version}}-macos11/Python_Framework.pkg/Versions/{python_major_dot_minor_version}" && \
        export CFLAGS="--target=x86_64-apple-darwin -isysroot /osxcross/target/SDK/MacOSX11.1.sdk -I$PYTHON_ROOT/include/python{python_major_dot_minor_version} -I$PYTHON_ROOT/Headers" && \
        export LDFLAGS="-isysroot /osxcross/target/SDK/MacOSX11.1.sdk -Wl,-syslibroot,/osxcross/target/SDK/MacOSX11.1.sdk -L$PYTHON_ROOT/lib -lpython{python_major_dot_minor_version}" \
        && '''

def fix_EXT_SUFFIX(cp_version, new_base_os, new_dist_target):
    """
    Generate the command to fix the EXT_SUFFIX for cross builds.
    This is necessary to ensure that the built library can be imported correctly.
    Place this command AFTER the build command.

    Parameters:
    - cp_version (str): The CP version to use in the filename.
    - new_base_os (str): The new base OS for the library (target name in .so files).
    - new_dist_target (str): The new distribution target.

    Returns:
    - str: The command to fix the EXT_SUFFIX.
    """

    return f''' && cd dist && \
        orig_whl=$(ls *-cp{cp_version}-cp{cp_version}-linux_x86_64.whl) && \
        unzip -o *-cp{cp_version}-cp{cp_version}-linux_x86_64.whl -d tmp && cd tmp && \
        find . -type f -name "*.cpython-{cp_version}-x86_64-linux-gnu.so" -exec bash -c 'mv "$0" "${{0/-x86_64-linux-gnu/-{new_base_os}}}"' {{}} \\; && \
        sed -i 's/linux_x86_64/{new_dist_target}/g' *.dist-info/WHEEL && \
        sed -i 's/x86_64-linux-gnu/{new_base_os}/g' *.dist-info/RECORD && \
        zip -r "../${{orig_whl/-linux_x86_64/-{new_dist_target}}}" * && \
        cd .. && rm -rf *-cp{cp_version}-cp{cp_version}-linux_x86_64.whl tmp/ ../clang-wrapper.sh'''

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
            python_major_dot_minor_version = ".".join(python_version.split(".")[:2])

            if target == 'manylinux_2_17_x86_64':

                image_name = f"manylinux-lvl3-cp{cp_version}-manylinux_2_17"
                original_dist_target = "linux_x86_64"
                new_dist_target = "manylinux_2_17_x86_64.manylinux2014_x86_64"

                # build the library
                if build != None:

                    build_command = wrapper_python("python3") + wrapper_pip("pip3") + build + rename_dist(original_dist_target, new_dist_target)

                    print(f">> Building the library for cp-{cp_version}-{target}")
                    run_lvl3_image(image_name, build_command, host_workspace_path, logfile)

                # test the library
                if test != None:

                    test_command = install_dist(cp_version, new_dist_target) + wrapper_python("python3") + wrapper_pip("pip3") + test

                    print(f">> Testing the library for cp-{cp_version}-{target}")
                    run_lvl3_image(image_name, test_command, host_workspace_path, None)

            if target == 'musllinux_1_2_x86_64':

                image_name = f"musllinux-lvl3-cp{cp_version}-musllinux_1_2"
                original_dist_target = "linux_x86_64"
                new_dist_target = "musllinux_1_2_x86_64"

                # build the library
                if build != None:

                    build_command = wrapper_python("python3") + wrapper_pip("pip3") + build + rename_dist(original_dist_target, new_dist_target)

                    print(f">> Building the library for cp-{cp_version}-{target}")
                    run_lvl3_image(image_name, build_command, host_workspace_path, logfile)

                # test the library
                if test != None:

                    test_command = install_dist(cp_version, new_dist_target) + wrapper_python("python3") + wrapper_pip("pip3") + test

                    print(f">> Testing the library for cp-{cp_version}-{target}")
                    run_lvl3_image(image_name, test_command, host_workspace_path, None)

            if target == 'win_amd64':

                image_name = f"win-macosx-pookie-lvl3-cp{cp_version}-win"
                new_python_command = f"wine /python*/*/python*/python.exe"
                new_pip_command = f"wine /python*/*/python*/python.exe -m pip"

                # build the library
                if build != None:

                    build_command = wrapper_python3(new_python_command) + wrapper_python(new_python_command) + wrapper_pip3(new_pip_command) + wrapper_pip(new_pip_command) + build

                    print(f">> Building the library for cp-{cp_version}-{target}")
                    run_lvl3_image(image_name, build_command, host_workspace_path, logfile)

            if target == 'macosx_11_0_x86_64':

                image_name = f"win-macosx-pookie-lvl3-cp{cp_version}-macosx"
                new_base_os = "darwin"
                new_dist_target = "macosx_11_0_x86_64"

                # build the library
                if build != None:

                    build_command = prepare_environment_macosx_11_0_x86_64(python_major_dot_minor_version) + wrapper_python("python3") + wrapper_pip("pip3") + build + fix_EXT_SUFFIX(cp_version, new_base_os, new_dist_target)

                    print(f">> Building the library for cp-{cp_version}-{target}")
                    run_lvl3_image(image_name, build_command, host_workspace_path, logfile)

                # test the library
                if test != None:

                    print(f">> Testing the library for cp-{cp_version}-{target}")
                    print("Not supported yet :(")