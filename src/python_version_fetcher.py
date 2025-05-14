import requests
import re
from collections import defaultdict

TARGET_MAPPING = {
    "manylinux_2_17_x86_64": "x86_64-unknown-linux-gnu",
    "musllinux_1_2_x86_64": "x86_64-unknown-linux-musl",
    "win_amd64": "x86_64-pc-windows-msvc",
    "macosx_11_0_x86_64": "x86_64-apple-darwin"
}

def get_latest_release_urls(minors, targets):
    """
    Fetches the latest release URLs for specified Python minor versions and targets.

    Parameters:
    - minors: List of minor versions to fetch (e.g., ['10', '12']).
    - targets: List of target platforms to fetch (e.g., ['manylinux_2_17_x86_64', 'win_amd64']).

    Returns:
    - A dictionary with minor versions as keys and dictionaries of target URLs as values.
      Each target dictionary contains the filename, download URL, and release tag.
    """
    url = "https://api.github.com/repos/astral-sh/python-build-standalone/releases/latest"
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch latest release: {response.status_code}")

    release = response.json()
    tag = release["tag_name"]
    assets = release.get("assets", [])

    platforms_regex = '|'.join(re.escape(TARGET_MAPPING[t]) for t in targets if t in TARGET_MAPPING)
    pattern = re.compile(
        rf"^cpython-3\.(\d+)\.\d+\+\d+-({platforms_regex})-install_only\.tar\.gz$"
    )

    platform_lookup = {v: k for k, v in TARGET_MAPPING.items() if k in targets}
    temp_results = defaultdict(dict)

    for asset in assets:
        name = asset["name"]
        match = pattern.match(name)
        if not match:
            continue

        minor = match.group(1)
        platform = match.group(2)
        target = platform_lookup.get(platform)

        if target:
            temp_results[minor][target] = {
                "filename": name,
                "url": asset["browser_download_url"],
                "tag": tag
            }

    if minors is None:
        sorted_minors = sorted(temp_results.keys(), key=lambda x: int(x))
        selected_minors = sorted_minors[-4:]
    else:
        selected_minors = [str(m) for m in minors]

    results = {minor: temp_results[minor] for minor in selected_minors if minor in temp_results}

    return results

def main():
    minors = ['10', '12']
    targets = [
        "manylinux_2_17_x86_64",
        "musllinux_1_2_x86_64",
        "win_amd64",
        "macosx_11_0_x86_64"
    ]

    results = get_latest_release_urls(minors, targets)

    if not results:
        print("No matching assets found in latest release.")
        return

    for minor, target_data in results.items():
        print(f"\nPython 3.{minor}.x:")
        for target, info in target_data.items():
            print(f"  Target: {target}")
            print(f"    Filename: {info['filename']}")
            print(f"    Release tag: {info['tag']}")
            print(f"    Download URL: {info['url']}")
        print()

    print(results)

if __name__ == "__main__":
    main()
