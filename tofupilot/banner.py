"""TofuPilot client banner utilities."""

from importlib.metadata import PackageNotFoundError

import logging

import requests
from packaging import version
from importlib.metadata import version as version_of_package

def print_banner_and_check_version() -> None:

    logger_name = "tofupilot"
    logger = logging.getLogger(logger_name)

    current_version = version_of_package("tofupilot")

    print_version_banner(current_version)

    check_latest_version(logger, current_version, "tofupilot")

def print_version_banner(current_version: str) -> None:
    """Print the TofuPilot client version banner."""
    yellow = "\033[33m"
    blue = "\033[34m"
    reset = "\033[0m"

    cap = f"{blue}╭{reset} {yellow}✈{reset} {blue}╮{reset}"
    tofu = "[•ᴗ•]"
    spac = "     "

    banner = (
        f"{cap } \n"
        f"{tofu} TofuPilot Python Client {current_version}\n"
        f"{spac} \n"
    )

    print(banner, end="")

import posthog
from .error_tracking import ApiVersionWarning


def check_latest_version(logger, current_version, package_name: str):
    """Checks if the package is up-to-date and emits a warning if not"""
    try:
        response = requests.get(
            f"https://pypi.org/pypi/{package_name}/json", timeout=10
        )
        response.raise_for_status()
        latest_version = response.json()["info"]["version"]

        try:
            if version.parse(current_version) < version.parse(latest_version):
                warning_message = (
                    f"You are using {package_name} version {current_version}, however version {latest_version} is available. "
                    f'You should consider upgrading via the "pip install --upgrade {package_name}" command.'
                )
                posthog.capture_exception(ApiVersionWarning(warning_message))
                logger.warning(warning_message)
        except PackageNotFoundError as e:
            posthog.capture_exception(e)
            logger.info(f"Package not installed: {package_name}")

    except requests.RequestException as e:
        posthog.capture_exception(e)
        logger.warning("Failed to check version, more information in debug logs")
        logger.debug(f"Error checking version: While connecting to PyPI: {e}")
