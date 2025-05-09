# Contributing to Project

First off, thanks for taking the time to contribute!

## Code of Conduct

This project adheres to the Contributor Covenant [code of conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to support@tofupilot.com.

## How to Contribute

### Reporting Bugs

If you find a bug, please open an issue [here](https://github.com/tofupilot/python-client/issues) with detailed information on how to reproduce it.

### Suggesting Features

You can suggest new features by opening an issue [here](https://github.com/tofupilot/python-client/issues).

### Submitting Pull Requests

1. Fork the repository.
2. Create a new branch (e.g., `feature/xyz`).
3. Make your changes.
4. Commit your changes **following the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) format** to ensure correct tagging, release notes, and changelog:
   - `fix:` for bug fixes (SemVer patch).
   - `feat:` for new features (SemVer minor).
   - `feat!:`, `fix!:`, etc., for breaking changes (SemVer major).
5. Push to your branch.
6. Create a pull request [here](https://github.com/tofupilot/python-client/pulls).

## Development Setup

To set up a local development environment:

1. Clone the repo
   ```bash
   git clone https://github.com/tofupilot/python-client.git
   ```
2. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

## Style Guide

Please follow PEP 8 guidelines for Python code.

## Testing

To run tests, use:

```bash
pytest
```

## How is the package published?

TofuPilot is available on [PyPI](https://pypi.org/project/tofupilot/). Version publishing is handled via [release-please](https://github.com/googleapis/release-please) and [Twine](https://twine.readthedocs.io/en/stable/) through GitHub Actions.

To better understand how this works, you can read the release-please documentation, the [`release-please.yml` file](https://github.com/tofupilot/python-client/blob/main/.github/workflows/release-please.yml), and the [`python-publish.yml` file](https://github.com/tofupilot/python-client/blob/main/.github/workflows/python-publish.yml).

In summary, when new commits are added to `main` and are considered “releasable units” (e.g., a commit with a `"feat"` or `"fix"` prefix), a new release PR is automatically created by release-please. The changelog and the version number in `setup.py` are also updated by release-please, and a tag and release commit are created.

When the release PR is merged, and a new release is detected by the “Python publish” Github workflow, a new version of the TofuPilot package is uploaded to PyPI.

### Testing the Python Client locally

1. Create a new branch for testing your changes.  
2. Apply any changes to the code as needed.  
3. In `setup.py`, update the following line:  
   ```python
   version="X.Y.Z"
   ```  
   to:  
   ```python
   version="X.Y.Z.dev0"
   ```

4. Run:  
   ```sh
   rm -rf dist/*
   ```

5. Run:  
   ```sh
   python -m build
   ```

6. Install your new version locally in your project [using pip](https://packaging.python.org/en/latest/tutorials/installing-packages/#installing-from-a-local-src-tree)

### Releasing a test version of the Python Client

If you need to test a new version of the Python client before making an official release, you can publish it to TestPyPI, a sandbox version of PyPI used for testing package distributions.

1. If a previous test package with the exact same version was released, update the version in `setup.py`. For instance, change version="X.Y.Z.dev0" to version="X.Y.Z.dev1".
2. Build the package locally using:
   ```sh
   rm -rf dist/*
   python -m build
   ```
   This will generate distribution files in the dist/ directory.

3. Get a testpypi API key, for example ask your managment if they have one.

   Then run:
   ```sh
   twine upload --repository testpypi dist/*
   ```
 
4. To install the new test package, run:
   ```sh
   pip install -i https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ tofupilot==<exact-version>
   ```

### Releasing a production version of the Python Client

Only members of the TofuPilot team can merge the release PR into `main`, which triggers a new release and an upload to PyPI.

However, contributions are always welcome! If you'd like to help improve the project, feel free to open an issue or submit a pull request. We appreciate your input.