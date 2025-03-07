import argparse
import os
import subprocess

def main():
    parser = argparse.ArgumentParser(description='Tool for Automating the Build and Testing Process of Native Python Libraries Using Cross-Compilation and Emulation Technologies')

    parser.add_argument('source', type=str, help='Python library to build and test')
    parser.add_argument('--build', action='store_true', help='Build the library')
    parser.add_argument('--test', action='store_true', help='Test the library')
    parser.add_argument('--python-version', type=str, default='3.13.1', help='Python version to use (default: 3.13.1)')
    parser.add_argument('--target', type=str, required=True, nargs='+', choices=['x86_64-linux', 'x86_64-windows', 'x86_64-macos', 'arm64-macos'], help='Target platform(s) to build and test the library')

    args = parser.parse_args()

    if not os.path.isfile(args.source):
        print(f"Error: {args.source} is not a valid file.")
        return

    for target in args.target:
        if target == 'x86_64-linux':

            subprocess.run([
                'docker', 'build', '-f', f'Dockerfile.{target}',
                '--build-arg', f'PYTHON_VERSION={args.python_version}',
                '--build-arg', f'C_SOURCE_FILE={args.source}',
                '-t', f'{target}', '.'
            ])

            compiled = os.path.splitext(args.source)[0] + ".so"
            subprocess.run([
                'docker', 'run', '-it', '--rm',
                '-v', f'{os.getcwd()}/workspace:/workspace',
                f'{target}', '/bin/bash', '-c',
                f'gcc -shared -o {compiled} -fPIC {args.source} $(python3-config --cflags --ldflags) && cp {compiled} /workspace'
            ])

if __name__ == '__main__':
    main()