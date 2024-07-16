import warnings
import requests
from packaging import version
from importlib.metadata import version as get_version, PackageNotFoundError

def check_latest_version(logger, package_name: str):
    try:
        response = requests.get(f'https://pypi.org/pypi/{package_name}/json')
        response.raise_for_status()
        latest_version = response.json()['info']['version']
        
        try:
            installed_version = get_version(package_name)
            if version.parse(installed_version) < version.parse(latest_version):
                warning_message = (
                    f'You are using {package_name} version {installed_version}, however version {latest_version} is available. '
                    f'You should consider upgrading via the "pip install --upgrade {package_name}" command.'
                )
                warnings.warn(warning_message, UserWarning)
                logger.warning(warning_message)
        except PackageNotFoundError:
            logger.info(f"Package {package_name} is not installed.")
    
    except requests.RequestException as e:
        logger.warning(f"Error checking the latest version: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
