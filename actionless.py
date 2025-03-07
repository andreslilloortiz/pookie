import argparse
import os

def main():
    parser = argparse.ArgumentParser(description='Tool for Automating the Build and Testing Process of Native Python Libraries Using Cross-Compilation and Emulation Technologies')

    parser.add_argument('package', type=str, help='Python package to build and test')
    parser.add_argument('--build', action='store_true', help='Build the package')
    parser.add_argument('--test', action='store_true', help='Test the package')
    parser.add_argument('--python-version', type=str, default='3.13', help='Python version to use (default: 3.13)')
    parser.add_argument('--target', type=str, required=True, nargs='+', choices=['x86_64-linux', 'x86_64-windows', 'x86_64-macos', 'arm64-macos'], help='Target platform(s) to build and test the package')

    args = parser.parse_args()

    if not os.path.isfile(args.package):
        print(f"Error: {args.package} is not a valid file.")
        return

    print(args.package)
    print(args.python_version)
    if args.build:
        print(f'build')
    elif args.test:
        print(f'test')
    else:
        print('build and test')

    for target in args.target:
        print(target)

if __name__ == '__main__':
    main()