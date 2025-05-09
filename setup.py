from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as file:
    long_description = file.read()

setup(
    name="tofupilot",
    version="1.9.3",
    packages=find_packages(),
    install_requires=["requests", "setuptools", "packaging", "websockets"],
    author="Félix Berthier",
    author_email="felix.berthier@tofupilot.com",
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
