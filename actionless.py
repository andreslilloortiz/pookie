import argparse
import os
import subprocess

def main():
    parser = argparse.ArgumentParser(description='Tool for Automating the Build and Testing Process of Native Python Libraries Using Cross-Compilation and Emulation Technologies')

    parser.add_argument('--build',
                            type = str,
                            help = 'Python library to build')
    parser.add_argument('--test',
                            type = str,
                            help = 'Test file to run after building the library')
    parser.add_argument('--python-version',
                            type = str,
                            nargs = '+',
                            choices = ['3.13.2', '3.12.9', '3.11.9', '3.10.11'],
                            default = ['3.13.2', '3.12.9', '3.11.9', '3.10.11'],
                            help = 'Python version(s) to use (default: all)')
    parser.add_argument('--target',
                            type = str,
                            nargs = '+',
                            choices = ['x86_64-linux', 'x86_64-windows', 'x86_64-macos', 'arm64-macos'],
                            default = ['x86_64-linux', 'x86_64-windows', 'x86_64-macos', 'arm64-macos'],
                            help = 'Target platform(s) to build and test the library (default: all)')

    args = parser.parse_args()

    # check args
    print(">> Configuration")
    for arg in vars(args):
        print(f"- {arg}: {getattr(args, arg)}")

    # copy files to workspace
    subprocess.run([
        'mkdir',
            '-p',
            'workspace'
        ])

    if args.build != None and os.path.isfile(args.build):
        subprocess.run([
            'cp',
                args.build,
                'workspace'
        ])

    if args.test != None and os.path.isfile(args.test):
        subprocess.run([
            'cp',
                args.test,
                'workspace'
        ])

    # build only one docker image for all architectures and python versions of windows and macos
    if any("windows" in item.lower() for item in args.target):
        # create windows docker image
        print(f">> Creating docker image for all-all-windows")
        subprocess.run([
            'docker',
                'build',
                '-f',
                    f'images/Dockerfile.all-windows',
                '-t',
                    f'all-all-windows',
                '.'
        ])

    if any("macos" in item.lower() for item in args.target):
        # create macos docker image
        print(f">> Creating docker image for all-all-macos")
        subprocess.run([
            'docker',
                'build',
                '-f',
                    f'images/Dockerfile.all-macos',
                '-t',
                    f'all-all-macos',
                '.'
        ])

    # build only one docker image for all python versions of x86_64-linux
    if any("x86_64-linux" in item.lower() for item in args.target):
        # create x86_64-linux docker image
        print(f">> Creating docker image for all-x86_64-linux")
        subprocess.run([
            'docker',
                'build',
                '-f',
                    f'images/Dockerfile.x86_64-linux',
                '-t',
                    f'all-x86_64-linux',
                '.'
        ])

    # iterate versions and targets for build and test the library
    for target in args.target:
        for python_version in args.python_version:

            # x86_64-linux
            if target == 'x86_64-linux':

                subprocess.run([
                    'mkdir',
                        '-p',
                        f'workspace/{python_version}-{target}'
                ])

                # build the library
                if args.build != None and os.path.isfile(args.build):

                    print(f">> Building the library for {python_version}-{target}")
                    compiled = os.path.splitext(args.build)[0] + ".so"
                    subprocess.run([
                        'docker',
                            'run',
                            '-it',
                            '--rm',
                            '-v',
                                f'{os.getcwd()}/workspace:/workspace',
                            f'all-{target}',
                            '/bin/bash',
                                '-c',
                                f'cd /workspace && gcc -shared -o {compiled} -fPIC {args.build} $(python3-config --cflags --ldflags) && mv {compiled} {python_version}-{target}'
                    ])

                # test the library
                if args.test != None and os.path.isfile(args.test):

                    print(f">> Testing the library for {python_version}-{target}")
                    subprocess.run([
                        'docker',
                            'run',
                            '-it',
                            '--rm',
                            '-v',
                                f'{os.getcwd()}/workspace:/workspace',
                            f'all-{target}',
                            '/bin/bash',
                                '-c',
                                f'cd workspace && cp {args.test} {python_version}-{target} && cd {python_version}-{target} && python3 {args.test} && rm {args.test}'
                    ])

            # x86_64-windows
            if target == 'x86_64-windows':

                # PYTHONHASHSEED=1
                '''
                CL_PATH='/my_msvc/opt/msvc/bin/x64/cl.exe'
                INCLUDE_PATH='/python-3.13.2-x86_64-windows/include'
                LIB_PATH='/python-3.13.2-x86_64-windows/libs'
                PYTHON_PATH='/python-3.13.2-x86_64-windows/python.exe'
                '''

                subprocess.run([
                    'mkdir',
                        '-p',
                        f'workspace/{python_version}-{target}'
                ])

                # build the library
                if args.build != None and os.path.isfile(args.build):
                    pass

                # test the library
                if args.test != None and os.path.isfile(args.test):
                    pass

    print("\n>> Check the workspace directory for the compiled library")

if __name__ == '__main__':
    main()