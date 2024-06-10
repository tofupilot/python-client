# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
