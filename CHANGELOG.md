<!-- markdownlint-disable MD012 MD013 MD024 MD033 -->
# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/) and this project adheres to [Semantic Versioning](https://semver.org/)

## [1.2.0] 2025-04-22

### Added

- ask command
  - `--output` / `-o` with default value `-` for stdout
- proper test suite

## [1.1.0] 2025-04-18

### Added

- proper logging
- JSON output now includes qname and IRI of the question
  - only if dataset has a prefix and query an ID
- more questions file validation
  - break if non-unique IDs
  - break if only a few quesions have IDs

## [1.0.1] 2025-04-15

### Fixed

- include needed dependency

## [1.0.0] 2025-04-15

### Added

- initial version

