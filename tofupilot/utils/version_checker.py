from importlib.metadata import PackageNotFoundError

import requests
from packaging import version

from ..constants import SECONDS_BEFORE_TIMEOUT
from .tofu_art import print_version_warning


def check_latest_version(current_version: str, package_name: str):
    """Checks if the package is up-to-date and prints a warning if not"""
    try:
        response = requests.get(f"https://pypi.org/pypi/{package_name}/json", timeout=SECONDS_BEFORE_TIMEOUT)
        response.raise_for_status()
        latest_version = response.json()["info"]["version"]

        try:
            if version.parse(current_version) < version.parse(latest_version):
                print_version_warning(current_version, latest_version, package_name)
        except PackageNotFoundError:
            pass  # Package not installed, skip warning

    except requests.RequestException:
        pass  # Version check failed, skip warning
