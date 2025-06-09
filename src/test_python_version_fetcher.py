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