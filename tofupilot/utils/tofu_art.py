"""Tofu art and banner utilities."""


def print_tofu_banner(current_version: str):
    """Print current version of client with tofu art."""
    yellow = "\033[33m"
    blue = "\033[34m"
    reset = "\033[0m"

    banner = f"{blue}╭{reset} {yellow}✈{reset} {blue}╮{reset}\n[•ᴗ•] TofuPilot Python Client {current_version}\n"
    print(banner)


def print_version_warning(current_version: str, latest_version: str, package_name: str):
    """Print version upgrade warning with tofu prefix."""
    warning_prefix = "TP:WRN"
    warning_message = (
        f"{warning_prefix} You are using {package_name} version {current_version}, "
        f"however version {latest_version} is available. "
        f'You should consider upgrading via the "pip install --upgrade {package_name}" command.'
    )
    print(warning_message)
