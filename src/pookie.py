import argparse
import os
import subprocess
from python_version_fetcher import find_latest_patch_versions
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
    print(">> Fetching python versions from python.org")
    required_files = []
    for target in args.target:
        # map target to required files
        if target == 'manylinux_2_17_x86_64' or target == 'musllinux_1_2_x86_64' or target == 'macosx_11_0_x86_64':
            required_files.append('tar_xz')
        if target == 'win_amd64':
            required_files.append('exe')
        if target == 'macosx_11_0_x86_64':
            required_files.append('pkg')

    python_versions_dic = find_latest_patch_versions(3, args.python_version, required_files)
    print(">> Python versions fetched")
    for python_version, urls_dic in python_versions_dic.items():
        print(f"- {".".join(python_version.split(".")[:2])}:")
        for url_type, url in urls_dic.items():
            print(f"  - {url_type}: {url}")

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

    # # iterate versions and targets for build and test the library
    # for target in args.target:
    #     for python_version in args.python_version:

    #         # x86_64-linux
    #         if target == 'x86_64-linux':

    #             # build the library
    #             if args.build != None:

    #                 subprocess.run([
    #                     'mkdir',
    #                         '-p',
    #                         f'/workspace/{python_version}-{target}'
    #                 ], stdout=logfile, stderr=logfile)

    #                 print(f">> Building the library for {python_version}-{target}")
    #                 subprocess.run([
    #                     'docker',
    #                         'run',
    #                         '-it',
    #                         '--rm',
    #                         '-v',
    #                             f'{host_workspace_path}:/workspace',
    #                         f'all-{target}',
    #                         '/bin/bash',
    #                             '-c',
    #                             f'source /myenv{python_version}/bin/activate && python3 -m pip install -U setuptools wheel build && cd /workspace && python3 -m build && rm -rf {python_version}-{target}/dist {python_version}-{target}/*.egg-info && mv dist *.egg-info {python_version}-{target} && deactivate'
    #                 ], stdout=logfile, stderr=logfile)

    #             # test the library
    #             if args.test != None:

    #                 print(f">> Testing the library for {python_version}-{target} with '{args.test}'")

    #                 subprocess.run([
    #                     'docker',
    #                         'run',
    #                         '-it',
    #                         '--rm',
    #                         '-v',
    #                             f'{host_workspace_path}:/workspace',
    #                         f'all-{target}',
    #                         '/bin/bash',
    #                             '-c',
    #                             f'source myenv{python_version}/bin/activate && cd workspace && python3 -m pip install {python_version}-{target}/dist/*.whl >> /dev/null 2>> /dev/null && {args.test} && deactivate'
    #                 ])

    #         # x86_64-windows
    #         if target == 'x86_64-windows':

    #             # build the library
    #             if args.build != None:

    #                 subprocess.run([
    #                     'mkdir',
    #                         '-p',
    #                         f'/workspace/{python_version}-{target}'
    #                 ], stdout=logfile, stderr=logfile)

    #                 print(f">> Building the library for {python_version}-{target}")
    #                 compiled = os.path.splitext(args.build[0])[0] + ".pyd"
    #                 lpython = int(python_version.split('.')[0] + python_version.split('.')[1])

    #                 build_file_content = f"""@echo off\n/python-{python_version}-{target}/python.exe -m venv myenv{python_version}\ncall myenv{python_version}/Scripts/activate.bat\n/mingw64/bin/gcc.exe -shared -o {compiled} {builds} -I "/python-{python_version}-{target}/include" -L "/python-{python_version}-{target}/libs" -lpython{lpython}"""

    #                 with open(f"tmp.bat", 'w') as build_file:
    #                     build_file.write(build_file_content)

    #                 subprocess.run([
    #                     'docker',
    #                         'run',
    #                         '-it',
    #                         '--rm',
    #                         '-v',
    #                             f'{host_workspace_path}:/workspace',
    #                         '-w',
    #                             '/workspace',
    #                         'all-all-windows',
    #                         'wine',
    #                             'cmd',
    #                                 '/c',
    #                                     f'tmp.bat && move {compiled} {python_version}-{target} && rmdir /S /Q myenv{python_version} && del /Q tmp.bat && exit'
    #                 ], stdout=logfile, stderr=logfile)

    #             # test the library
    #             if args.test != None:

    #                 print(f">> Testing the library for {python_version}-{target} with '{args.test}'")

    #                 test_command = re.sub(r'\bpython3?\b', '$PYTHON_DIR', args.test)

    #                 subprocess.run([
    #                     'docker',
    #                         'run',
    #                         '-it',
    #                         '--rm',
    #                         '-v',
    #                             f'{host_workspace_path}:/workspace',
    #                         'all-all-windows',
    #                         '/bin/bash',
    #                             '-c',
    #                             f'PYTHON_DIR=/python-{python_version}-{target}/python.exe && cd workspace && cp {python_version}-{target}/*.pyd . && export PYTHONHASHSEED=0 && WINEDEBUG=-all wine {test_command} 2>&1 | grep -v -E "wine" && rm *.pyd'
    #                 ])

    #         # x86_64-macos
    #         if target == 'x86_64-macos':

    #             # build the library
    #             if args.build != None:

    #                 subprocess.run([
    #                     'mkdir',
    #                         '-p',
    #                         f'/workspace/{python_version}-{target}'
    #                 ], stdout=logfile, stderr=logfile)

    #                 print(f">> Building the library for {python_version}-{target}")
    #                 compiled = os.path.splitext(args.build[0])[0] + ".so"
    #                 subfolder = ".".join(python_version.split(".")[:2])
    #                 subprocess.run([
    #                     'docker',
    #                         'run',
    #                         '-it',
    #                         '--rm',
    #                         '-v',
    #                             f'{host_workspace_path}:/workspace',
    #                         'all-all-macos',
    #                         '/bin/bash',
    #                             '-c',
    #                             f'cd /workspace && o64-clang -shared -o {compiled} -undefined dynamic_lookup -I/python-{python_version}-x86_64-macos/include/python{subfolder} {builds} && mv {compiled} {python_version}-{target}'
    #                 ], stdout=logfile, stderr=logfile)

    #             # test the library
    #             if args.test != None:

    #                 print(f">> Testing the library for {python_version}-{target} with '{args.test }'")
    #                 print("Not yet supported :(")

    print(">> See you soon")

if __name__ == '__main__':
    main()
