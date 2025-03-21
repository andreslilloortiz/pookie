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
                            choices = ['3.13.1', '3.12.9', '3.11.9', '3.10.10'],
                            default = ['3.13.1', '3.12.9', '3.11.9', '3.10.10'],
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

    # build only one docker for windows and macos
    if any("windows" in item.lower() for item in args.target):
        # create docker image
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
        # create docker image
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

    # iterate versions and targets
    for target in args.target:
        for python_version in args.python_version:

            # x86_64-linux
            if target == 'x86_64-linux':

                subprocess.run([
                    'mkdir',
                        '-p',
                        f'workspace/{python_version}-{target}'
                ])

                # create docker image
                print(f">> Creating docker image for {python_version}-{target}")
                subprocess.run([
                    'docker',
                        'build',
                        '-f',
                            f'images/Dockerfile.{target}',
                        '--build-arg',
                            f'PYTHON_VERSION={python_version}',
                        '-t',
                            f'{python_version}-{target}',
                        '.'
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
                            f'{python_version}-{target}',
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
                            f'{python_version}-{target}',
                            '/bin/bash',
                                '-c',
                                f'cd workspace && cp {args.test} {python_version}-{target} && cd {python_version}-{target} && python3 {args.test} && rm {args.test}'
                    ])

            # x86_64-windows
            if target == 'x86_64-windows':

                # PYTHONHASHSEED=1

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