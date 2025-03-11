from importlib.metadata import PackageNotFoundError

import requests
import sys
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
        minimal_python_version = response.json()["info"]["requires_python"]
        current_python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

        try:
            if version.parse(current_version) < version.parse(latest_version):
                warning_message = (
                    f"You are using {package_name} version {current_version}, however version {latest_version} is available. "
                    f'You should consider upgrading via the "pip install --upgrade {package_name}" command.\n'
                    f"You may need to upgrade Python first. You current version of Python is {current_python_version} and the latest version of tofupilot needs at least {minimal_python_version}"
                )
                logger.warning(warning_message)
        except PackageNotFoundError:
            logger.info(f"Package {package_name} is not installed.")

    except requests.RequestException as e:
        logger.warning(f"Error checking the latest version: {e}")
