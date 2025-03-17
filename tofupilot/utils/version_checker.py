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
                    f" You are using {package_name} version {current_version}, however version {latest_version} is available. "
                    f'You should consider upgrading via the "pip install --upgrade {package_name}" command.\n'
                    f"You may need to upgrade Python first. You current version of Python is {current_python_version} and the latest version of tofupilot needs at least {minimal_python_version}"
                )
                logger.warning(warning_message)
            if sys.version_info.major == 2:
                logger.error(
                    f"ERROR: Python {current_python_version} is no longer supported. Please upgrade to Python {minimal_python_version} or later to use this client."
                )
            # all tofupilot versions need at least Python 3.6
            elif version.parse(current_python_version) < version.parse("3.5"):
                logger.warning(
                    f" WARNING: Your Python version {current_python_version} is outdated. Some features may not work correctly. Consider upgrading to Python {minimal_python_version}."
                )
        except PackageNotFoundError:
            logger.info(f"Package {package_name} is not installed.")

    except requests.RequestException as e:
        logger.warning(f"Error checking the latest version: {e}")
