import argparse
import os
import subprocess

def main():
    parser = argparse.ArgumentParser(description='Tool for Automating the Build and Testing Process of Native Python Libraries Using Cross-Compilation and Emulation Technologies')

    parser.add_argument('--build', type=str, help='Python library to build')
    parser.add_argument('--test', type=str, help='Test file to run after building the library')
    parser.add_argument('--python-version', type=str, default='3.13.1', help='Python version to use (default: 3.13.1)')
    parser.add_argument('--target', type=str, required=True, nargs='+', choices=['x86_64-linux', 'x86_64-windows', 'x86_64-macos', 'arm64-macos'], help='Target platform(s) to build and test the library')

    args = parser.parse_args()

    # check args
    for arg in vars(args):
        print(f"{arg}: {getattr(args, arg)}")

    # move files to workspace
    subprocess.run(['mkdir', '-p', 'workspace'])
    if args.build != None and os.path.isfile(args.build):    
        subprocess.run(['cp', args.build, 'workspace'])
    if args.test != None and os.path.isfile(args.test):
        subprocess.run(['cp', args.test, 'workspace'])

    # iterate targets
    for target in args.target:

        # x86_64-linux
        if target == 'x86_64-linux':

            # create docker image
            print(">> Creating docker image for x86_64-linux")
            subprocess.run([
                'docker', 'build', '-f', f'images/Dockerfile.{target}',
                '--build-arg', f'PYTHON_VERSION={args.python_version}',
                '-t', f'{args.python_version}-{target}', '.'
            ])

            # build the library
            if args.build != None and os.path.isfile(args.build):

                print(">> Building the library for x86_64-linux")
                compiled = os.path.splitext(args.build)[0] + ".so"
                subprocess.run([
                    'docker', 'run', '-it', '--rm',
                    '-v', f'{os.getcwd()}/workspace:/workspace',
                    f'{args.python_version}-{target}', '/bin/bash', '-c',
                    f'cd /workspace && gcc -shared -o {compiled} -fPIC {args.build} $(python3-config --cflags --ldflags)'
                ])

            # test the library
            if args.test != None and os.path.isfile(args.test):

                print(">> Testing the library for x86_64-linux")
                subprocess.run([
                    'docker', 'run', '-it', '--rm',
                    '-v', f'{os.getcwd()}/workspace:/workspace',
                    f'{args.python_version}-{target}', '/bin/bash', '-c',
                    f'cd /workspace && python3 {args.test}'
                ])

    print(">> Check the workspace directory for the compiled library")

if __name__ == '__main__':
    main()