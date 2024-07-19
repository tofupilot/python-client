# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2024-07-19

### Added

- `steps` parameter in client.create_run method to reflect TofuPilot's API update

## [1.0.0] - 2024-07-16

### Added

- LICENSE.md file
- CONTRIBUTING.md file
- CODE_OF_CONDUCT.md file
- Unitary tests in new tests/ folder
- Functional tests in new examples/ folder
- Docstring for the client’s create_run method
- Github action for automatic testing
- Github action for automatic release in Pypi

### Fixed

- Replaced deprecated package pkg_resources with a maintained alternative

### Changed

- Open-sourced the repository
- Made API key readable from environment
- Detailed the project in README.md
- Standardized and enhanced logging output for better readability

## [0.1.20] - 2024-06-28

### Changed

- renamed "params" to "report_variables"

## [0.1.19] - 2024-06-28

### Changed

- Made the “duration” parameter of the client optional to match the API
- Made the client.create_run method return an object containing only the run URL, not its ID

## [0.1.18] - 2024-06-28

### Added

- Option to add different base URL to the client

## [0.1.17] - 2024-06-28

### Fixed

- Removed example client code

## [0.1.16] - 2024-06-28

### Added

- Handling of file attachments

### Changed

- Removed the "test_function" parameter and replaced it with an API wrapper

## [0.1.15] - 2024-06-26

### Changed

- Moved "params" parameter of the client to the optional return value of "test_function"

## [0.1.14] - 2024-06-20

### Fixed

- Fixed client call to use localhost instead of the TP website

## [0.1.13] - 2024-06-20

### Changed

- Updated the signature of the client’s create_run method to match the new TofuPilot API format

## [0.1.12] - 2024-06-17

### Added

- Logging of all calls to stdout or stderr in test_function

## [0.1.11] - 2024-06-13

### Added

- "raw_response" parameter to the create_run method

### Changed

- Error messages are now formatted as: { "error": error_msg }

## [0.1.10] - 2024-06-13

### Changed

- Return type of the create_run method

## [0.1.9] - 2024-06-10

### Fixed

- Imports

## [0.1.8] - 2024-06-10

### Added

- Missing requirements

## [0.1.7] - 2024-06-10

### Added

- Print and logging of the run URL before returning it
- Package version check
- Hid all attributes of TofuPilotClient except the create_run method

## [0.1.6] - 2024-06-10

### Changed

- Removed base_url parameter from TofuPilotClient constructor
- Renamed method create_test_run to create_run
- Made "component_revision" parameter of method create_run optional to match TofuPilot API

## [0.1.5] - 2024-06-10

### Changed

- Improved error messages
- Added custom exception class (TofuPilotClientError)
- Logging of errors

## [0.1.4] - 2024-06-07

### Added

- MANIFEST.in file

## [0.1.3] - 2024-06-07

### Added

- CHANGELOG.md file

### Changed

- Transfered repository to the tofupilot organization
