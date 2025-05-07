from importlib.metadata import PackageNotFoundError

import requests
from packaging import version
from ..constants import SECONDS_BEFORE_TIMEOUT


def check_latest_version(logger, current_version, package_name: str):
    """Checks if the package is up-to-date and emits a warning if not"""
    try:
        response = requests.get(
            f"https://pypi.org/pypi/{package_name}/json", timeout=SECONDS_BEFORE_TIMEOUT
        )
        response.raise_for_status()
        latest_version = response.json()["info"]["version"]

        try:
            if version.parse(current_version) < version.parse(latest_version):
                # Direct printing with warning color (yellow) but without the TP:WRN prefix
                yellow = "\033[0;33m"
                reset = "\033[0m"
                print(f"\n{yellow}Update available: {package_name} {current_version} → {latest_version}{reset}")
                print(f"{yellow}Run: pip install --upgrade {package_name}{reset}\n")
                
                # We don't use logger.warning here to avoid the colored TP:WRN prefix
        except PackageNotFoundError:
            # Silently ignore package not found errors
            pass

    except requests.RequestException:
        # Silently ignore connection errors during version check
        pass
