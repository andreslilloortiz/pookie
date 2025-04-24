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

def check_files(version):
    """
    Checks if the necessary files (`Python-<version>.tar.xz`,
    `python-<version>-embed-amd64.zip`, and `python-<version>-macos11.pkg`) are
    available for a specific version on the Python FTP server.

    Parameters:
    - version (str): The specific Python version to check for the files.

    Returns:
    - A tuple containing the full URLs for the `.tar.xz`, `.zip`, and `.pkg` files
      if all files are available, or `None` if any file is missing.
    """
    url = f"{BASE_URL}{version}/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    files = [a['href'] for a in soup.find_all("a", href=True)]

    tar_xz = f"Python-{version}.tar.xz"
    embed_zip = f"python-{version}-embed-amd64.zip"
    macos_pkg = f"python-{version}-macos11.pkg"

    if tar_xz in files and embed_zip in files and macos_pkg in files:
        return (url + tar_xz, url + embed_zip, url + macos_pkg)

    return None

def find_latest_patch_versions(major_version, minor_versions=None):
    """
    Finds the latest available patch versions for specific minor versions
    within the major version, ensuring that all necessary files
    (`.tar.xz`, `.zip`, and `.pkg`) are present for those versions.

    If no minor_versions are provided, it will use the latest 4 minor versions.

    Parameters:
    - major_version (int): The major version to search for.
    - minor_versions (list, optional): A list of minor versions to search for.

    Returns:
    - A dictionary where the keys are the minor versions and the values are lists
      of URLs for the files of the latest patch version in each minor version.
      If no valid version is found for a minor version, the value is an empty list.
    """
    # If minor_versions is not provided, fetch the latest 4 available minor versions
    if not minor_versions:
        # Get all available versions for the major_version
        response = requests.get(BASE_URL)
        soup = BeautifulSoup(response.text, "html.parser")
        all_versions = set()

        for a in soup.find_all("a", href=True):
            match = re.match(rf"{major_version}\.(\d+)\.\d+/?", a['href'])
            if match:
                all_versions.add(match.group(1))

        # Select the latest 4 minor versions
        minor_versions = sorted(map(int, all_versions), reverse=True)[:4]

    result = {}

    for minor_version in minor_versions:
        versions = get_versions(major_version, minor_version)
        files_found = []

        for version in versions:
            files = check_files(version)
            if files:
                files_found = files
                break  # Found the latest valid version for this minor version

        result[minor_version] = files_found

    return result
