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
    return f''' && pip install auditwheel && python -m auditwheel repair dist/*-{original_dist_target}.whl --plat {new_dist_target} --only-plat -w dist && rm -f dist/*-{original_dist_target}.whl'''

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

def prepare_environment_macosx_11_0_x86_64_and_macosx_11_0_arm64(cross_compiler, arquitecture, python_major_dot_minor_version):
    """
    Generate the command to prepare the environment for macosx_11_0_x86_64 and macosx_11_0_arm64 builds.
    This includes setting up the compiler and linker flags.
    Place this command BEFORE the build command.

    Parameters:
    - python_major_dot_minor_version (str): The major and minor version of Python to use (e.g., "3.12").

    Returns:
    - str: The command to prepare the environment.
    """

    return f'''export LDSHARED="$(pwd)/clang-wrapper.sh -shared" && \
        echo -e "#!/bin/bash\nexec {cross_compiler} -fuse-ld=/osxcross/target/bin/{arquitecture}-apple-darwin20.2-ld \"\\$@\"" > clang-wrapper.sh && chmod +x clang-wrapper.sh && \
        export CC=$(pwd)/clang-wrapper.sh && \
        export CXX=$CC && \
        export AR={arquitecture}-apple-darwin20.2-ar && \
        export RANLIB={arquitecture}-apple-darwin20.2-ranlib && \
        export STRIP={arquitecture}-apple-darwin20.2-strip && \
        export CFLAGS="--target={arquitecture}-apple-darwin -isysroot /osxcross/target/SDK/MacOSX11.1.sdk -I/python/include/python{python_major_dot_minor_version}" && \
        export LDFLAGS="-isysroot /osxcross/target/SDK/MacOSX11.1.sdk -Wl,-syslibroot,/osxcross/target/SDK/MacOSX11.1.sdk -L/python/lib -lpython{python_major_dot_minor_version}" \
        && '''

def prepare_environment_manylinux_2_17_x86_64_and_musllinux_1_2_x86_64(CC, CXX):
    """
    Generate the command to prepare the environment for manylinux_2_17_x86_64 and musllinux_1_2_x86_64 builds.
    Place this command BEFORE the build command.

    Parameters:
    - CC (str): The C compiler to use.
    - CXX (str): The C++ compiler to use.

    Returns:
    - str: The command to prepare the environment.
    """

    return f'''export CC={CC} && export CXX={CXX} && '''

def prepare_environment_win_amd64(py_version_nodot, python_major_dot_minor_version):
    """
    Generate the command to prepare the environment for win_amd64 builds.
    This includes setting up the compiler and linker flags.
    Place this command BEFORE the build command.

    Parameters:
    - py_version_nodot (str): The major and minor version of Python to use (e.g., "312").
    - python_major_dot_minor_version (str): The major and minor version of Python to use (e.g., "3.12").

    Returns:
    - str: The command to prepare the environment.
    """

    return f'''cat <<'EOF' > mingw-wrapper.sh
#!/bin/bash

# Detect if we're in the linking phase by checking for `-shared` flag
if [[ "$@" == *"-shared"* ]]; then
    # Reorder args: move `-lpython{py_version_nodot}` and enable auto-import to the end
    args=()
    libs=()
    for arg in "$@"; do
        if [[ "$arg" == "-lpython{py_version_nodot}" ]]; then
            libs+=("$arg")
        elif [[ "$arg" == "-Wl,--enable-auto-import" ]]; then
            libs+=("$arg")
        else
            args+=("$arg")
        fi
    done
    # Now call the real compiler
    exec x86_64-w64-mingw32-gcc "${{args[@]}}" "${{libs[@]}}"
else
    # Not linking: compile as usual
    exec x86_64-w64-mingw32-gcc "$@"
fi
EOF

cat <<EOF > /python_cross/lib/python{python_major_dot_minor_version}/site-packages/sitecustomize.py
import distutils.util
import sysconfig
import setuptools.command.bdist_wheel as bdist_wheel_mod

# Patch platform functions
distutils.util.get_platform = lambda: "win-amd64"
sysconfig.get_platform = lambda: "win-amd64"

# Patch get_tag()
def _patched_get_tag(self):
    return 'cp{py_version_nodot}', 'cp{py_version_nodot}', 'win_amd64'

bdist_wheel_mod.bdist_wheel.get_tag = _patched_get_tag
EOF

    chmod +x ./mingw-wrapper.sh && \
    export PYTHONPATH=/python_cross/lib/python{python_major_dot_minor_version}/site-packages
    export CC="$(pwd)/mingw-wrapper.sh" && \
    export CXX="$CC" && \
    export CFLAGS="-I/python/include" && \
    export LDFLAGS="-L/python/libs -lpython{py_version_nodot} -Wl,--enable-auto-import" \
    &&
'''

def fix_Wheel_macosx_11_0_x86_64_and_macosx_11_0_arm64(py_version_nodot, new_dist_target):
    """
    Generate the command to fix the wheel platform and tags for macosx_11_0_x86_64 and macosx_11_0_arm64 cross builds.
    This is necessary to ensure that the built library can be imported correctly.
    Place this command AFTER the build command.

    Parameters:
    - py_version_nodot (str): The CP version to use in the filename.
    - new_dist_target (str): The new distribution target.

    Returns:
    - str: The command to fix the EXT_SUFFIX.
    """

    return f''' && cd dist && \
        orig_whl=$(ls *-cp{py_version_nodot}-cp{py_version_nodot}-linux_x86_64.whl) && \
        unzip -o *-cp{py_version_nodot}-cp{py_version_nodot}-linux_x86_64.whl -d tmp && cd tmp && \
        sed -i 's/linux_x86_64/{new_dist_target}/g' *.dist-info/WHEEL && \
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
            '--privileged',
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

def run_docker_images(targets, logfile, python_versions_dic, build, test, linux_x86_64_compiler, linux_non_native_mode, host_workspace_path):
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

                image_name = f"manylinux-lvl3-cp{py_version_nodot}-manylinux_2_17_x86_64"
                original_dist_target = "linux_x86_64"
                new_dist_target = "manylinux2014_x86_64.manylinux_2_17_x86_64"

                if linux_x86_64_compiler == 'gcc':
                    CC = "gcc"
                    CXX = "g++"
                else:
                    CC = "clang"
                    CXX = "clang++"

                # build the library
                if build != None:

                    build_command = \
                        prepare_environment_manylinux_2_17_x86_64_and_musllinux_1_2_x86_64(CC, CXX) + \
                        build + \
                        rename_dist(original_dist_target, target)

                    print(f">> Building the library for cp-{py_version_nodot}-{target}")
                    run_lvl3_image(image_name, build_command, host_workspace_path, logfile)

                # test the library
                if test != None:

                    test_command = \
                        install_dist(py_version_nodot, new_dist_target) + \
                        test

                    print(f">> Testing the library for cp-{py_version_nodot}-{target}")
                    run_lvl3_image(image_name, test_command, host_workspace_path, None)

            if target == 'manylinux_2_17_aarch64':

                image_name = f"manylinux-lvl3-cp{py_version_nodot}-manylinux_2_17_aarch64"
                original_dist_target = "linux_aarch64"
                new_dist_target = "manylinux2014_aarch64.manylinux_2_17_aarch64"

                python_aarch64 = "LD_LIBRARY_PATH=/usr/aarch64-linux-gnu/lib /python/bin/python3"
                pip_aarch64 = "LD_LIBRARY_PATH=/usr/aarch64-linux-gnu/lib /python/bin/python3 -m pip"

                # build the library
                if build != None:

                    if linux_non_native_mode == 'cross':
                        build_command = \
                            build + \
                            rename_dist(original_dist_target, target)
                    else:
                        build_command = \
                            wrapper('python3', python_aarch64) + \
                            wrapper('python', python_aarch64) + \
                            wrapper('pip3', pip_aarch64) + \
                            wrapper('pip', pip_aarch64) + \
                            build + \
                            rename_dist(original_dist_target, target)

                    print(f">> Building the library for cp-{py_version_nodot}-{target}")
                    run_lvl3_image(image_name, build_command, host_workspace_path, logfile)

                # test the library
                if test != None:

                    test_command = \
                        wrapper('python3', python_aarch64) + \
                        wrapper('python', python_aarch64) + \
                        wrapper('pip3', pip_aarch64) + \
                        wrapper('pip', pip_aarch64) + \
                        install_dist(py_version_nodot, new_dist_target) + \
                        test

                    print(f">> Testing the library for cp-{py_version_nodot}-{target}")
                    run_lvl3_image(image_name, test_command, host_workspace_path, None)

            if target == "manylinux_2_17_armv7l":

                image_name = f"manylinux-lvl3-cp{py_version_nodot}-manylinux_2_17_armv7l"
                original_dist_target_cross = "linux_armv7"
                original_dist_target_emulate = "linux_armv7l"
                new_dist_target = "manylinux2014_armv7l.manylinux_2_17_armv7l"

                python_armv7 = "LD_LIBRARY_PATH=/usr/arm-linux-gnueabihf/lib /python/bin/python3"
                pip_armv7 = "LD_LIBRARY_PATH=/usr/arm-linux-gnueabihf/lib /python/bin/python3 -m pip"

                # build the library
                if build != None:

                    if linux_non_native_mode == 'cross':
                        build_command = \
                            build + \
                            rename_dist(original_dist_target_cross, target)
                    else:
                        build_command = \
                            wrapper('python3', python_armv7) + \
                            wrapper('python', python_armv7) + \
                            wrapper('pip3', pip_armv7) + \
                            wrapper('pip', pip_armv7) + \
                            build + \
                            rename_dist(original_dist_target_emulate, target)

                    print(f">> Building the library for cp-{py_version_nodot}-{target}")
                    run_lvl3_image(image_name, build_command, host_workspace_path, logfile)

                # test the library
                if test != None:

                    test_command = \
                        wrapper('python3', python_armv7) + \
                        wrapper('python', python_armv7) + \
                        wrapper('pip3', pip_armv7) + \
                        wrapper('pip', pip_armv7) + \
                        install_dist(py_version_nodot, new_dist_target) + \
                        test

                    print(f">> Testing the library for cp-{py_version_nodot}-{target}")
                    run_lvl3_image(image_name, test_command, host_workspace_path, None)

            if target == "manylinux_2_17_ppc64le":

                image_name = f"manylinux-lvl3-cp{py_version_nodot}-manylinux_2_17_ppc64le"
                original_dist_target = "linux_ppc64le"
                new_dist_target = "manylinux2014_ppc64le.manylinux_2_17_ppc64le"

                python_ppc64le = "LD_LIBRARY_PATH=/usr/powerpc64le-linux-gnu/lib /python/bin/python3"
                pip_ppc64le = "LD_LIBRARY_PATH=/usr/powerpc64le-linux-gnu/lib /python/bin/python3 -m pip"

                # build the library
                if build != None:

                    if linux_non_native_mode == 'cross':
                        build_command = \
                            build + \
                            rename_dist(original_dist_target, target)
                    else:
                        build_command = \
                            wrapper('python3', python_ppc64le) + \
                            wrapper('python', python_ppc64le) + \
                            wrapper('pip3', pip_ppc64le) + \
                            wrapper('pip', pip_ppc64le) + \
                            build + \
                            rename_dist(original_dist_target, target)

                    print(f">> Building the library for cp-{py_version_nodot}-{target}")
                    run_lvl3_image(image_name, build_command, host_workspace_path, logfile)

                # test the library
                if test != None:

                    test_command = \
                        wrapper('python3', python_ppc64le) + \
                        wrapper('python', python_ppc64le) + \
                        wrapper('pip3', pip_ppc64le) + \
                        wrapper('pip', pip_ppc64le) + \
                        install_dist(py_version_nodot, new_dist_target) + \
                        test

                    print(f">> Testing the library for cp-{py_version_nodot}-{target}")
                    run_lvl3_image(image_name, test_command, host_workspace_path, None)

            if target == "manylinux_2_17_s390x":

                image_name = f"manylinux-lvl3-cp{py_version_nodot}-manylinux_2_17_s390x"
                original_dist_target = "linux_s390x"
                new_dist_target = "manylinux2014_s390x.manylinux_2_17_s390x"

                python_s390x = "LD_LIBRARY_PATH=/usr/s390x-linux-gnu/lib /python/bin/python3"
                pip_s390x = "LD_LIBRARY_PATH=/usr/s390x-linux-gnu/lib /python/bin/python3 -m pip"

                # build the library
                if build != None:

                    if linux_non_native_mode == 'cross':
                        build_command = \
                            build + \
                            rename_dist(original_dist_target, target)
                    else:
                        build_command = \
                            wrapper('python3', python_s390x) + \
                            wrapper('python', python_s390x) + \
                            wrapper('pip3', pip_s390x) + \
                            wrapper('pip', pip_s390x) + \
                            build + \
                            rename_dist(original_dist_target, target)

                    print(f">> Building the library for cp-{py_version_nodot}-{target}")
                    run_lvl3_image(image_name, build_command, host_workspace_path, logfile)

                # test the library
                if test != None:

                    test_command = \
                        wrapper('python3', python_s390x) + \
                        wrapper('python', python_s390x) + \
                        wrapper('pip3', pip_s390x) + \
                        wrapper('pip', pip_s390x) + \
                        install_dist(py_version_nodot, new_dist_target) + \
                        test

                    print(f">> Testing the library for cp-{py_version_nodot}-{target}")
                    run_lvl3_image(image_name, test_command, host_workspace_path, None)

            if target == 'musllinux_1_2_x86_64':

                image_name = f"musllinux-lvl3-cp{py_version_nodot}-musllinux_1_2_x86_64"
                original_dist_target = "linux_x86_64"
                new_dist_target = "musllinux_1_2_x86_64"

                if linux_x86_64_compiler == 'gcc':
                    CC = "gcc"
                    CXX = "g++"
                else:
                    CC = "clang"
                    CXX = "clang++"

                # build the library
                if build != None:

                    build_command = \
                        prepare_environment_manylinux_2_17_x86_64_and_musllinux_1_2_x86_64(CC, CXX) + \
                        build + \
                        rename_dist(original_dist_target, target)

                    print(f">> Building the library for cp-{py_version_nodot}-{target}")
                    run_lvl3_image(image_name, build_command, host_workspace_path, logfile)

                # test the library
                if test != None:

                    test_command = \
                        install_dist(py_version_nodot, new_dist_target) + \
                        test

                    print(f">> Testing the library for cp-{py_version_nodot}-{target}")
                    run_lvl3_image(image_name, test_command, host_workspace_path, None)

            if target == 'win_amd64':

                image_name = f"win-macosx-pookie-lvl3-cp{py_version_nodot}-win_amd64"

                # build the library
                if build != None:

                    build_command = \
                        prepare_environment_win_amd64(py_version_nodot, python_major_dot_minor_version) + \
                        build

                    print(f">> Building the library for cp-{py_version_nodot}-{target}")
                    run_lvl3_image(image_name, build_command, host_workspace_path, logfile)

                # test the library
                if test != None:

                    print(f">> Testing the library for cp-{py_version_nodot}-{target}")
                    print("Not supported yet :(")

            if target == 'macosx_11_0_x86_64':

                image_name = f"win-macosx-pookie-lvl3-cp{py_version_nodot}-macosx_11_0_x86_64"
                new_dist_target = "macosx_11_0_x86_64"
                cross_compiler = "o64-clang"
                arquitecture = "x86_64"

                # build the library
                if build != None:

                    build_command = \
                        prepare_environment_macosx_11_0_x86_64_and_macosx_11_0_arm64(cross_compiler, arquitecture, python_major_dot_minor_version) + \
                        build + \
                        fix_Wheel_macosx_11_0_x86_64_and_macosx_11_0_arm64(py_version_nodot, new_dist_target)

                    print(f">> Building the library for cp-{py_version_nodot}-{target}")
                    run_lvl3_image(image_name, build_command, host_workspace_path, logfile)

                # test the library
                if test != None:

                    print(f">> Testing the library for cp-{py_version_nodot}-{target}")
                    print("Not supported yet :(")

            if target == 'macosx_11_0_arm64':

                image_name = f"win-macosx-pookie-lvl3-cp{py_version_nodot}-macosx_11_0_arm64"
                new_dist_target = "macosx_11_0_arm64"
                cross_compiler = "oa64-clang"
                arquitecture = "arm64"

                # build the library
                if build != None:

                    build_command = \
                        prepare_environment_macosx_11_0_x86_64_and_macosx_11_0_arm64(cross_compiler, arquitecture, python_major_dot_minor_version) + \
                        build + \
                        fix_Wheel_macosx_11_0_x86_64_and_macosx_11_0_arm64(py_version_nodot, new_dist_target)

                    print(f">> Building the library for cp-{py_version_nodot}-{target}")
                    run_lvl3_image(image_name, build_command, host_workspace_path, logfile)

                # test the library
                if test != None:

                    print(f">> Testing the library for cp-{py_version_nodot}-{target}")
                    print("Not supported yet :(")