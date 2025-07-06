from datetime import datetime
from setuptools import setup, find_packages


def get_version():
    """Get version using date-based format."""
    # Try to read from _version.py if created by CI/CD
    try:
        version_globals = {}
        with open("_version.py", "r") as f:
            exec(f.read(), version_globals)
        return version_globals["__version__"]
    except (FileNotFoundError, KeyError):
        pass
    
    # Default: generate date-based version for local development
    now = datetime.now()
    return f"{now.year}.{now.month}.{now.day}.dev{now.hour:02d}{now.minute:02d}"


setup(
    name="tofupilot",
    version=get_version(),
    description="A client library for accessing TofuPilot API v1",
    packages=find_packages(),
    package_data={
        "tofupilot": ["**/py.typed"],
    },
    include_package_data=True,
    install_requires=[
        "httpx>=0.23.0,<0.29.0",
        "attrs>=22.2.0",
        "python-dateutil>=2.8.0",
    ],
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)