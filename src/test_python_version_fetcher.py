# This file is part of pookie.

# Copyright (C) 2025 Andrés Lillo Ortiz

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

from unittest.mock import patch
from python_version_fetcher import get_latest_release_urls

@patch("python_version_fetcher.requests.get")
def test_minors_none_latest_four(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        "tag_name": "v1.0.0",
        "assets": [
            {"name": "cpython-3.9.1+123-x86_64-unknown-linux-gnu-install_only.tar.gz", "browser_download_url": "url_9"},
            {"name": "cpython-3.10.1+123-x86_64-unknown-linux-gnu-install_only.tar.gz", "browser_download_url": "url_10"},
            {"name": "cpython-3.11.1+123-x86_64-unknown-linux-gnu-install_only.tar.gz", "browser_download_url": "url_11"},
            {"name": "cpython-3.12.1+123-x86_64-unknown-linux-gnu-install_only.tar.gz", "browser_download_url": "url_12"},
            {"name": "cpython-3.13.1+123-x86_64-unknown-linux-gnu-install_only.tar.gz", "browser_download_url": "url_13"},
        ]
    }

    result = get_latest_release_urls(None, ["manylinux_2_17_x86_64"])
    assert sorted(result.keys()) == ["10", "11", "12", "13"]

@patch("python_version_fetcher.requests.get")
def test_exact_version_and_platform(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        "tag_name": "v1.0.0",
        "assets": [
            {"name": "cpython-3.10.5+123-x86_64-unknown-linux-gnu-install_only.tar.gz", "browser_download_url": "my_url"}
        ]
    }

    result = get_latest_release_urls(["10"], ["manylinux_2_17_x86_64"])
    assert result == {
        "10": {
            "manylinux_2_17_x86_64": {
                "filename": "cpython-3.10.5+123-x86_64-unknown-linux-gnu-install_only.tar.gz",
                "url": "my_url",
                "tag": "v1.0.0"
            }
        }
    }

@patch("python_version_fetcher.requests.get")
def test_no_matching_versions(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        "tag_name": "v1.0.0",
        "assets": []
    }

    result = get_latest_release_urls(["10"], ["manylinux_2_17_x86_64"])
    assert result == {}