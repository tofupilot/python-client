from setuptools import setup, find_packages

setup(
    name="tofupilot",
    version="0.1.18",
    packages=find_packages(),
    install_requires=[
        "requests",
        "setuptools",
        "packaging"
    ],
    author="Félix Berthier",
    author_email="felix.berthier@tofupilot.com",
    description="The official python client for the TofuPilot API",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url="https://github.com/tofupilot/python-client",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
