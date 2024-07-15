import requests
import pkg_resources
from packaging import version
import warnings

def check_latest_version(logger, package_name: str):
    try:
        response = requests.get(f'https://pypi.org/pypi/{package_name}/json')
        response.raise_for_status()
        latest_version = response.json()['info']['version']
        installed_version = pkg_resources.get_distribution(package_name).version
        if version.parse(installed_version) < version.parse(latest_version):
            warnings.warn(
                f'You are using {package_name} version {installed_version}, however version {latest_version} is available. '
                f'You should consider upgrading via the "pip install --upgrade {package_name}" command.',
                UserWarning
            )
    except requests.RequestException as e:
        logger.warning(f"Error checking the latest version: {e}")
    except pkg_resources.DistributionNotFound:
        logger.info(f"Package {package_name} is not installed.")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")