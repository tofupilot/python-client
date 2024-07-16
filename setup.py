from setuptools import setup, find_packages

setup(
    name="tofupilot",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "requests",
        "setuptools",
        "packaging"
    ],
    author="Félix Berthier",
    author_email="felix.berthier@tofupilot.com",
    description="The official Python client for the TofuPilot API",
    license = "MIT",
    keywords = "automatic hardware testing tofupilot",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url="https://github.com/tofupilot/python-client",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
