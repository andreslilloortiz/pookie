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
                            choices = ['3.13.2', '3.12.9', '3.11.11', '3.10.16'],
                            default = ['3.13.2', '3.12.9', '3.11.11', '3.10.16'],
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
        print(f"\t- {arg}: {getattr(args, arg)}")

    # move files to workspace
    subprocess.run(['mkdir', '-p', 'workspace'])
    if args.build != None and os.path.isfile(args.build):
        subprocess.run(['cp', args.build, 'workspace'])
    if args.test != None and os.path.isfile(args.test):
        subprocess.run(['cp', args.test, 'workspace'])

    # iterate versions and targets
    for python_version in args.python_version:
        print("\n>> Python version:", python_version)
        for target in args.target:

            # x86_64-linux
            if target == 'x86_64-linux':

                # create docker image
                print(f"\t- Creating docker image for {target}")
                subprocess.run([
                    'docker', 'build', '-f', f'images/Dockerfile.{target}',
                    '--build-arg', f'PYTHON_VERSION={python_version}',
                    '-t', f'{python_version}-{target}', '.'
                ])

                # build the library
                if args.build != None and os.path.isfile(args.build):

                    print(f"\t- Building the library for {target}")
                    compiled = os.path.splitext(args.build)[0] + ".so"
                    subprocess.run([
                        'docker', 'run', '-it', '--rm',
                        '-v', f'{os.getcwd()}/workspace:/workspace',
                        f'{python_version}-{target}', '/bin/bash', '-c',
                        f'cd /workspace && gcc -shared -o {compiled} -fPIC {args.build} $(python3-config --cflags --ldflags)'
                    ])

                # test the library
                if args.test != None and os.path.isfile(args.test):

                    print(f"\t- Testing the library for {target}")
                    subprocess.run([
                        'docker', 'run', '-it', '--rm',
                        '-v', f'{os.getcwd()}/workspace:/workspace',
                        f'{python_version}-{target}', '/bin/bash', '-c',
                        f'cd /workspace && python3 {args.test}'
                    ])

    print("\n>> Check the workspace directory for the compiled library")

if __name__ == '__main__':
    main()