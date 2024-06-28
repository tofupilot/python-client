# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.16] - 2024-06-28

### Fixed

- Removed example client code

## [0.1.16] - 2024-06-28

### Added

- Handling of file attachments

### Changed

- Removed "test_function" parameter to replace it by API wrapper

## [0.1.15] - 2024-06-26

### Changed

- Moved "params" parameter of client to optional return value of "test_function".

## [0.1.14] - 2024-06-20

### Fixed

- Fixed call of client from localhost and not TP website.

## [0.1.13] - 2024-06-20

### Changed

- Changed signature or client's create_run method to match new TofuPilot API format.

## [0.1.12] - 2024-06-17

### Added

- Logging of any call to stdout or stderr in test_function

## [0.1.11] - 2024-06-13

### Added

- "raw_response" parameter to create_run method

### Changed

- Message of error format like so: { "error": error_msg }

## [0.1.10] - 2024-06-13

### Changed

- Return type of create_run method

## [0.1.9] - 2024-06-10

### Fixed

- Imports

## [0.1.8] - 2024-06-10

### Added

- Missing requirements

## [0.1.7] - 2024-06-10

### Added

- Print and logging of run url before returning it
- Check of package version
- Hid all attributes of TofuPilotClient except create_run method

## [0.1.6] - 2024-06-10

### Changed

- Removed base_url param from TofuPilotClient constructor
- Renamed method create_test_run to create_run
- Made param 'component_revision' of method create_run optional to match TofuPilot API

## [0.1.5] - 2024-06-10

### Changed

- Better error messages
- Custom Exception class (TofuPilotClientError)
- Logging of errors to avoid use of try / catch statements around client

## [0.1.4] - 2024-06-07

### Added

- MANIFEST.in file

## [0.1.3] - 2024-06-07

### Added

- CHANGELOG.md file

### Changed

- Transfered repo to tofupilot organization
