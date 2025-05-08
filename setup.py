from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as file:
    long_description = file.read()

setup(
    name="tofupilot",
    version="1.11.1",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0",
        "setuptools>=50.0.0",
        "packaging>=20.0",
        "paho-mqtt>=2.0.0",
        "sentry-sdk>=1.0.0",
        "certifi>=2020.12.5",
    ],
    entry_points={
        "pytest11": [
            "tofupilot = tofupilot.plugin",  # Registering the pytest plugin
        ],
    },
    author="TofuPilot Team",
    author_email="hello@tofupilot.com",
    description="Official Python client for TofuPilot with OpenHTF integration, real-time streaming and file attachment support",
    license="MIT",
    keywords="automatic hardware testing tofupilot openhtf",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tofupilot/python-client",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Manufacturing",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.9",
)
