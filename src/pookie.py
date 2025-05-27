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

import argparse
import glob
import os
import subprocess
import sys
from python_version_fetcher import get_latest_release_urls
from docker_images_builder import build_docker_images
from docker_images_runner import run_docker_images

def main():
    parser = argparse.ArgumentParser(description='Tool for Automating the Build and Testing Process of Native Python Libraries Using Cross-Compilation and Emulation Technologies')

    targets = ['manylinux_2_17_x86_64', 'manylinux_2_17_aarch64', 'manylinux_2_17_armv7l', 'manylinux_2_17_ppc64le' , 'manylinux_2_17_s390x', 'musllinux_1_2_x86_64', 'win_amd64', 'macosx_11_0_x86_64', "macosx_11_0_arm64"] #TODO manylinux_2_17_riscv64 with riscv64-linux-gnu-gcc

    parser.add_argument(
        '--clean',
        action='store_true',
        help='Remove all build artifacts and end the script execution'
        )
    parser.add_argument(
        '--build',
        type = str,
        help = 'Python build bash command'
        )
    parser.add_argument(
        '--test',
        type = str,
        help = 'Python test bash command'
        )
    parser.add_argument(
        '--python-version',
        type = str,
        nargs = '+',
        help = 'Minor Python version(s) to compile for (default: last 4 available)'
        )
    parser.add_argument(
        '--target',
        type = str,
        nargs = '+',
        choices = targets,
        default = targets,
        help = 'Target platform(s) to build and test the library for (default: all)'
        )
    parser.add_argument(
        '--linux-x86_64-compiler',
        type=str,
        choices=['gcc', 'clang'],
        default='gcc',
        help='Compiler to use for manylinux_2_17_x86_64 or musllinux_1_2_x86_64 targets (default: gcc)'
        )
    parser.add_argument(
        '--linux-non-native-mode',
        type=str,
        choices=['cross', 'emulate'],
        default='cross',
        help='Compilation mode for non-native manylinux_2_17 targets (e.g. aarch64, armv7, ppc64le, riscv64, s390x): "cross" for cross-compilation or "emulate" for QEMU-based emulation (default: cross)'
        )

    args = parser.parse_args()

    # check args
    print(">> Configuration")
    for arg in vars(args):
        print(f"- {arg}: {getattr(args, arg)}")

    # Clean workspace if requested
    if (args.clean):
        print(">> Cleaning workspace")
        subprocess.run([
            'rm',
                '-rf',
                '__pycache__',
                'dist',
                'build'
        ]
        + glob.glob('*.egg-info'))
        print(">> See you soon")
        sys.exit()

    # Fetch python-versions
    print(">> Fetching python versions")
    python_versions_dic = get_latest_release_urls(args.python_version, args.target)
    if not python_versions_dic:
        print("No matching assets found in latest release.")
        return
    print(">> Python versions fetched")
    for minor, target_data in python_versions_dic.items():
        print(f"\nPython 3.{minor}.x:")
        for target, info in target_data.items():
            print(f"  Target: {target}")
            print(f"    Filename: {info['filename']}")
            print(f"    Release tag: {info['tag']}")
            print(f"    Download URL: {info['url']}")
    print()

    # log file
    logfile = open("pookie.log", "a")

    # build docker images
    build_docker_images(args.target, logfile, python_versions_dic)

    # workspace for docker in docker
    host_workspace_path = os.environ.get('WORKSPACE_PWD', '/workspace')

    # run build and test commands
    run_docker_images(args.target, logfile, python_versions_dic, args.build, args.test, args.linux_x86_64_compiler, args.linux_non_native_mode, host_workspace_path)

    # Delete __pycache__ folders
    subprocess.run([
        'rm',
            '-rf',
            '__pycache__'
    ])

    print(">> See you soon")

if __name__ == '__main__':
    main()
