import argparse
import os
import subprocess
import re

def image_exists(image_name):
    """Checks if a Docker image already exists."""
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

def main():
    parser = argparse.ArgumentParser(description='Tool for Automating the Build and Testing Process of Native Python Libraries Using Cross-Compilation and Emulation Technologies')


    parser.add_argument('--clean',
                            action='store_true',
                            help='Clean the workspace by removing all files and directories')
    parser.add_argument('--build',
                            type = str,
                            nargs = '+',
                            help = 'Python library source file(s) to build')
    parser.add_argument('--test',
                            type = str,
                            help = 'Test Python command to run after building the library')
    parser.add_argument('--python-version',
                            type = str,
                            nargs = '+',
                            choices = ['3.13.2', '3.12.9', '3.11.9', '3.10.11'],
                            default = ['3.13.2', '3.12.9', '3.11.9', '3.10.11'],
                            help = 'Python version(s) to compile for (if not specified: all)')
    parser.add_argument('--target',
                            type = str,
                            nargs = '+',
                            choices = ['x86_64-linux', 'x86_64-windows', 'x86_64-macos'],
                            default = ['x86_64-linux', 'x86_64-windows', 'x86_64-macos'],
                            help = 'Target platform(s) to build and test the library for (if not specified: all)')

    args = parser.parse_args()

    # check args
    print(">> Configuration")
    for arg in vars(args):
        print(f"- {arg}: {getattr(args, arg)}")

    # check --clean
    if args.clean:
        print(f">> Cleaning workspace")
        subprocess.run("find . -mindepth 1 ! -name '.keepme' -exec rm -rf {} +", shell=True)
        print(f">> See you soon")
        return

    # check --build
    builds = ""
    if args.build != None:
        for build in args.build:
            if not os.path.isfile(build):
                print(f">> WARNING: The specified build file '{build}' does not exist.")
            else:
                builds += " " + build
        builds.strip()

    # workspace for docker in docker
    host_workspace_path = os.environ.get('WORKSPACE_PWD', '/workspace')

    # log file
    logfile = open("pookie.log", "a")

    # build only one docker image for all python versions of x86_64-linux
    if any("x86_64-linux" in item.lower() for item in args.target):
        if not image_exists("all-x86_64-linux"):
            print(f">> Creating docker image for all-x86_64-linux")
            subprocess.run([
                'docker',
                    'build',
                    '-f',
                        '/Dockerfile.x86_64-linux',
                    '-t',
                        'all-x86_64-linux',
                    '.'
            ], stdout=logfile, stderr=logfile)
        else:
            print(">> Docker image for all-x86_64-linux is already built")

    # build only one docker image for all architectures and python versions of windows
    if any("windows" in item.lower() for item in args.target):
        if not image_exists("all-all-windows"):
            print(f">> Creating docker image for all-all-windows")
            subprocess.run([
                'docker',
                    'build',
                    '-f',
                        '/Dockerfile.all-windows',
                    '-t',
                        'all-all-windows',
                    '/python-prebuilt-binaries' # context
            ], stdout=logfile, stderr=logfile)
        else:
            print(">> Docker image for all-all-windows is already built")

    # build only one docker image for all architectures and python versions of macos
    if any("macos" in item.lower() for item in args.target):
        if not image_exists("all-all-macos"):
            print(f">> Creating docker image for all-all-macos")
            subprocess.run([
                'docker',
                    'build',
                    '-f',
                        '/Dockerfile.all-macos',
                    '-t',
                        'all-all-macos',
                    '/python-prebuilt-binaries' # context
            ], stdout=logfile, stderr=logfile)
        else:
            print(">> Docker image for all-all-macos is already built")

    # iterate versions and targets for build and test the library
    for target in args.target:
        for python_version in args.python_version:

            # x86_64-linux
            if target == 'x86_64-linux':

                # build the library
                if args.build != None:

                    subprocess.run([
                        'mkdir',
                            '-p',
                            f'/workspace/{python_version}-{target}'
                    ], stdout=logfile, stderr=logfile)

                    print(f">> Building the library for {python_version}-{target}")
                    subprocess.run([
                        'docker',
                            'run',
                            '-it',
                            '--rm',
                            '-v',
                                f'{host_workspace_path}:/workspace',
                            f'all-{target}',
                            '/bin/bash',
                                '-c',
                                f'source /myenv{python_version}/bin/activate && python3 -m pip install -U setuptools wheel build && cd /workspace && python3 -m build && rm -rf {python_version}-{target}/dist {python_version}-{target}/*.egg-info && mv dist *.egg-info {python_version}-{target} && deactivate'
                    ], stdout=logfile, stderr=logfile)

                # test the library
                if args.test != None:

                    print(f">> Testing the library for {python_version}-{target} with '{args.test}'")

                    subprocess.run([
                        'docker',
                            'run',
                            '-it',
                            '--rm',
                            '-v',
                                f'{host_workspace_path}:/workspace',
                            f'all-{target}',
                            '/bin/bash',
                                '-c',
                                f'source myenv{python_version}/bin/activate && cd workspace && python3 -m pip install {python_version}-{target}/dist/*.whl >> /dev/null 2>> /dev/null && {args.test} && deactivate'
                    ])

            # x86_64-windows
            if target == 'x86_64-windows':

                # build the library
                if args.build != None:

                    subprocess.run([
                        'mkdir',
                            '-p',
                            f'/workspace/{python_version}-{target}'
                    ], stdout=logfile, stderr=logfile)

                    print(f">> Building the library for {python_version}-{target}")
                    compiled = os.path.splitext(args.build[0])[0] + ".pyd"
                    lpython = int(python_version.split('.')[0] + python_version.split('.')[1])

                    build_file_content = f"""@echo off\n/python-{python_version}-{target}/python.exe -m venv myenv{python_version}\ncall myenv{python_version}/Scripts/activate.bat\n/mingw64/bin/gcc.exe -shared -o {compiled} {builds} -I "/python-{python_version}-{target}/include" -L "/python-{python_version}-{target}/libs" -lpython{lpython}"""

                    with open(f"tmp.bat", 'w') as build_file:
                        build_file.write(build_file_content)

                    subprocess.run([
                        'docker',
                            'run',
                            '-it',
                            '--rm',
                            '-v',
                                f'{host_workspace_path}:/workspace',
                            '-w',
                                '/workspace',
                            'all-all-windows',
                            'wine',
                                'cmd',
                                    '/c',
                                        f'tmp.bat && move {compiled} {python_version}-{target} && rmdir /S /Q myenv{python_version} && del /Q tmp.bat && exit'
                    ], stdout=logfile, stderr=logfile)

                # test the library
                if args.test != None:

                    print(f">> Testing the library for {python_version}-{target} with '{args.test}'")

                    test_command = re.sub(r'\bpython3?\b', '$PYTHON_DIR', args.test)

                    subprocess.run([
                        'docker',
                            'run',
                            '-it',
                            '--rm',
                            '-v',
                                f'{host_workspace_path}:/workspace',
                            'all-all-windows',
                            '/bin/bash',
                                '-c',
                                f'PYTHON_DIR=/python-{python_version}-{target}/python.exe && cd workspace && cp {python_version}-{target}/*.pyd . && export PYTHONHASHSEED=0 && WINEDEBUG=-all wine {test_command} 2>&1 | grep -v -E "wine" && rm *.pyd'
                    ])

            # x86_64-macos
            if target == 'x86_64-macos':

                # build the library
                if args.build != None:

                    subprocess.run([
                        'mkdir',
                            '-p',
                            f'/workspace/{python_version}-{target}'
                    ], stdout=logfile, stderr=logfile)

                    print(f">> Building the library for {python_version}-{target}")
                    compiled = os.path.splitext(args.build[0])[0] + ".so"
                    subfolder = ".".join(python_version.split(".")[:2])
                    subprocess.run([
                        'docker',
                            'run',
                            '-it',
                            '--rm',
                            '-v',
                                f'{host_workspace_path}:/workspace',
                            'all-all-macos',
                            '/bin/bash',
                                '-c',
                                f'cd /workspace && o64-clang -shared -o {compiled} -undefined dynamic_lookup -I/python-{python_version}-x86_64-macos/include/python{subfolder} {builds} && mv {compiled} {python_version}-{target}'
                    ], stdout=logfile, stderr=logfile)

                # test the library
                if args.test != None:

                    print(f">> Testing the library for {python_version}-{target} with '{args.test }'")
                    print("Not yet supported :(")

    print(">> See you soon")

if __name__ == '__main__':
    main()
