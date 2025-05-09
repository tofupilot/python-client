from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as file:
    long_description = file.read()

setup(
    name="tofupilot",
    version="1.10.0",
    packages=find_packages(),
    install_requires=["requests", "setuptools", "packaging", "pytest", "websockets"],
    entry_points={
        "pytest11": [
            "tofupilot = tofupilot.plugin",  # Registering the pytest plugin
        ],
    },
    author="TofuPilot",
    author_email="hello@tofupilot.com",
    description="The official Python client for the TofuPilot API",
    license="MIT",
    keywords="automatic hardware testing tofupilot",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tofupilot/python-client",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
)
