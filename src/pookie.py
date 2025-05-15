import argparse
import os
import subprocess
from python_version_fetcher import get_latest_release_urls
from docker_images_builder import build_docker_images
from docker_images_runner import run_docker_images

def main():
    parser = argparse.ArgumentParser(description='Tool for Automating the Build and Testing Process of Native Python Libraries Using Cross-Compilation and Emulation Technologies')

    parser.add_argument('--build',
                            type = str,
                            help = 'Python build bash command')
    parser.add_argument('--test',
                            type = str,
                            help = 'Python test bash command')
    parser.add_argument('--python-version',
                            type = str,
                            nargs = '+',
                            help = 'Minor Python version(s) to compile for (if not specified: last 4 available)')
    parser.add_argument('--target',
                            type = str,
                            nargs = '+',
                            choices = ['manylinux_2_17_x86_64', 'musllinux_1_2_x86_64', 'win_amd64', 'macosx_11_0_x86_64'],
                            default = ['manylinux_2_17_x86_64', 'musllinux_1_2_x86_64', 'win_amd64', 'macosx_11_0_x86_64'],
                            help = 'Target platform(s) to build and test the library for (if not specified: all)')

    args = parser.parse_args()

    # check args
    print(">> Configuration")
    for arg in vars(args):
        print(f"- {arg}: {getattr(args, arg)}")

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
    run_docker_images(args.target, logfile, python_versions_dic, args.build, args.test, host_workspace_path)

    # Delete __pycache__ folders
    subprocess.run([
        'rm',
            '-rf',
            '__pycache__'
    ], stdout = logfile, stderr = logfile)

    print(">> See you soon")

if __name__ == '__main__':
    main()
