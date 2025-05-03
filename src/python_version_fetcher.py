import requests
from bs4 import BeautifulSoup
import re

BASE_URL = "https://www.python.org/ftp/python/"
WINPYTHON_BASE_URL = "https://sourceforge.net/projects/winpython/files/WinPython_{major}.{minor}/"

def get_versions(major_version, minor_version):
    """
    Fetches all patch versions for a given major and minor version from the Python FTP server.

    Parameters:
    - major_version (str): Major version of Python (e.g., "3").
    - minor_version (str): Minor version of Python (e.g., "10").

    Returns:
    - list: A sorted list of patch versions (e.g., ["3.10.0", "3.10.1", ...]).
    """
    response = requests.get(BASE_URL)
    soup = BeautifulSoup(response.text, "html.parser")
    versions = []
    for a in soup.find_all("a", href=True):
        match = re.match(rf"{major_version}\.{minor_version}\.\d+/?", a['href'])
        if match:
            versions.append(match.group(0).strip('/'))
    return sorted(versions, key=lambda s: list(map(int, s.split('.'))), reverse=True)

def get_winpython_exe(version):
    """
    Fetches the latest WinPython executable URL for a given version.

    Parameters:
    - version (str): The version of Python (e.g., "3.10.0").

    Returns:
    - str: The URL of the latest WinPython executable.
    """
    major, minor = version.split('.')[:2]
    url = WINPYTHON_BASE_URL.format(major=major, minor=minor)
    response = requests.get(url)
    if response.status_code != 200:
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    subfolders = []

    # Find all subfolders that match the version pattern
    for a in soup.find_all("a", href=True):
        folder_name = a.text.strip().strip('/')
        if re.match(rf"{major}\.{minor}\.\d+\.\d+", folder_name):
            subfolders.append(folder_name)

    if not subfolders:
        return None

    def extract_version_number(name):
        return list(map(int, name.split('.')))

    # Sort subfolders by version number in descending order
    subfolders = sorted(subfolders, key=extract_version_number, reverse=True)

    # Check each subfolder for the latest WinPython executable
    for folder in subfolders:
        folder_url = f"{url}{folder}/"
        sub_response = requests.get(folder_url)
        if sub_response.status_code != 200:
            continue

        # Parse the subfolder page
        sub_soup = BeautifulSoup(sub_response.text, "html.parser")
        for a in sub_soup.find_all("a", href=True):
            filename = a.text.strip()
            if re.match(rf"Winpython64-{folder}.*\.exe", filename):
                return f"https://sourceforge.net/projects/winpython/files/WinPython_{major}.{minor}/{folder}/{filename}"

    return None

def check_files(version, required_files):
    """
    Checks if the required files are available for a given version.

    Parameters:
    - version (str): The version of Python (e.g., "3.10.0").
    - required_files (list): List of required files (e.g., ["tar_xz", "exe", "pkg"]).

    Returns:
    - dict: A dictionary with the required files and their URLs if available, otherwise None.
    """
    url = f"{BASE_URL}{version}/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    files = [a['href'] for a in soup.find_all("a", href=True)]

    file_map = {
        "tar_xz": f"Python-{version}.tar.xz",
        "pkg": f"python-{version}-macos11.pkg",
    }

    result = {}

    # Check for the presence of required files
    for key in required_files:
        if key == "exe":
            win_url = get_winpython_exe(version)
            result[key] = win_url
        elif key in file_map:
            result[key] = url + file_map[key] if file_map[key] in files else None

    return result if all(result.values()) else None

def find_latest_patch_versions(major_version, minor_versions=None, required_files=None):
    """
    Finds the latest patch versions of Python for a given major version and optional minor versions.

    Parameters:
    - major_version (int): Major version of Python (e.g., 3).
    - minor_versions (list): List of minor versions to check (e.g., [10, 11]).
    - required_files (list): List of required files (e.g., ["tar_xz", "exe", "pkg"]).
    - If minor_versions is None, it will fetch the last 4 available minor versions.
    - If required_files is None, it will check for "tar_xz", "exe", and "pkg".

    Returns:
    - dict: A dictionary with the version as the key and a dictionary of required files and their URLs as the value.
    """
    if required_files is None:
        required_files = ["tar_xz", "exe", "pkg"]

    # Check if minor_versions is provided
    if not minor_versions:
        response = requests.get(BASE_URL)
        soup = BeautifulSoup(response.text, "html.parser")
        all_versions = set()

        # Find all minor versions available for the major version
        for a in soup.find_all("a", href=True):
            match = re.match(rf"{major_version}\.(\d+)\.\d+/?", a['href'])
            if match:
                all_versions.add(int(match.group(1)))

        # Sort and get the last 4 available minor versions
        valid_minor_versions = []
        for minor_version in sorted(all_versions, reverse=True):
            versions = get_versions(major_version, minor_version)
            for version in versions:
                if check_files(version, required_files):
                    valid_minor_versions.append(minor_version)
                    break
            if len(valid_minor_versions) == 4:
                break

        minor_versions = valid_minor_versions

    # Check for each minor version
    result = {}
    for minor_version in minor_versions:
        versions = get_versions(major_version, minor_version)
        for version in versions:
            files = check_files(version, required_files)
            if files:
                result[version] = files
                break

    return result

if __name__ == "__main__":
    # Example usage
    major_version = 3
    minor_versions = [11, 10]
    required_files = ["tar_xz", "exe", "pkg"]

    latest_versions = find_latest_patch_versions(major_version, minor_versions, required_files)
    for version, files in latest_versions.items():
        print(f"Version: {version}")
        for file_type, url in files.items():
            print(f"  {file_type}: {url}")