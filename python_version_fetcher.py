import requests
from bs4 import BeautifulSoup
import re

BASE_URL = "https://www.python.org/ftp/python/"

def get_versions(major_version, minor_version):
    """
    Retrieves all available Python versions from the server that match the given
    major_version and minor_version, and sorts them in descending order by their
    full version (major, minor, and patch).

    Parameters:
    - major_version (int): The major version to search for.
    - minor_version (int): The minor version for which the patch versions are being searched.

    Returns:
    - A sorted list of version strings matching the major and minor version, sorted
      in descending order.
    """
    response = requests.get(BASE_URL)
    soup = BeautifulSoup(response.text, "html.parser")
    versions = []
    for a in soup.find_all("a", href=True):
        # Filters versions that correspond to the major and minor version
        match = re.match(rf"{major_version}\.{minor_version}\.\d+/?", a['href'])
        if match:
            versions.append(match.group(0).strip('/'))
    return sorted(versions, key=lambda s: list(map(int, s.split('.'))), reverse=True)

def check_files(version, required_files):
    """
    Checks if the specified files are available for a specific version on the Python FTP server.

    Parameters:
    - version (str): The specific Python version to check for the files.
    - required_files (list): A list of required file types (e.g., ['tar_xz', 'embed_zip', 'macos_pkg']).

    Returns:
    - A dictionary indicating the availability of each required file and their URLs if available.
      If any required file is missing, returns None.
    """
    url = f"{BASE_URL}{version}/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    files = [a['href'] for a in soup.find_all("a", href=True)]

    file_map = {
        "tar_xz": f"Python-{version}.tar.xz",
        "embed_zip": f"python-{version}-embed-amd64.zip",
        "macos_pkg": f"python-{version}-macos11.pkg",
    }

    result = {key: (url + file_map[key] if file_map[key] in files else None) for key in required_files}

    return result if all(result.values()) else None

def find_latest_patch_versions(major_version, minor_versions=None, required_files=None):
    """
    Finds the latest available patch versions for specific minor versions
    within the major version, ensuring that the specified files are present.

    If no minor_versions are provided, it will use the latest 4 minor versions
    that have all the required files.

    Parameters:
    - major_version (int): The major version to search for.
    - minor_versions (list, optional): A list of minor versions to search for.
    - required_files (list, optional): A list of required file types (e.g., ['tar_xz', 'embed_zip', 'macos_pkg']).
      Defaults to all three file types.

    Returns:
    - A dictionary where the keys are the full versions (major.minor.patch) and the values are dictionaries
      with the required file types as keys and their corresponding URLs as values.
    """
    if required_files is None:
        required_files = ["tar_xz", "embed_zip", "macos_pkg"]

    if not minor_versions:
        # Get all available versions for the major_version
        response = requests.get(BASE_URL)
        soup = BeautifulSoup(response.text, "html.parser")
        all_versions = set()

        for a in soup.find_all("a", href=True):
            match = re.match(rf"{major_version}\.(\d+)\.\d+/?", a['href'])
            if match:
                all_versions.add(int(match.group(1)))

        # Check for the latest 4 minor versions that have valid files
        valid_minor_versions = []
        for minor_version in sorted(all_versions, reverse=True):
            versions = get_versions(major_version, minor_version)
            for version in versions:
                if check_files(version, required_files):
                    valid_minor_versions.append(minor_version)
                    break  # Stop checking once a valid version is found for this minor version
            if len(valid_minor_versions) == 4:
                break  # Stop once we have 4 valid minor versions

        minor_versions = valid_minor_versions

    result = {}

    for minor_version in minor_versions:
        versions = get_versions(major_version, minor_version)

        for version in versions:
            files = check_files(version, required_files)
            if files:
                # Use the full version as the key and the files dictionary as the value
                result[version] = files
                break  # Found the latest valid version for this minor version

    return result
