# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [0.7.0] - 2026-01-13

### Fixed

- Properly cast datetime values to Datetime in response classes Thanks @PPetar1 
- Fix ManufactuersResponse dataclass results field Thanks @PPetar1

### Updated

- dataclass creation performance optimizations with slots
- ResponseBase creation performance optimization

## [0.6.0] - 2025-11-26

### Added

- Query parameter validation
- Additional test coverage
- mypy typing coverage
- `py.typed` file

## [0.5.0] - 2025-10-31

### Updated

- Drop support for Python 3.9
- Added support for Python 3.14

### Added

- Additional checks to validate query parameters.
- Additional checks to prevent out of range identifiers.
- `TimeoutError` HTTP error exception.

## [0.4.0] - 2025-03-31

### Updated

- Client rate limiting functionality
- Drop support for Python 3.8
- Type annotations removing old `Dict` and `List` in favor of `dict` and `list`

### Added

- Mypy type checking
- `ServiceUnavailableError` HTTP error exception.
- `BadGatewayError` HTTP error exception.
- Separated `RateLimitError` and `HTTPRateLimitError` into separated exception.

## [0.3.0] - 2024-10-01

**Breaking changes**

### Added

- Added new methods for passing API key value through environment variable.
- Added new v3 `locations.latest()` and `parameters.latest()` methods.
- Updated `measurements.list()` methods to match new v3 measurements endpoints.

## [0.2.1] - 2024-02-15

### Fixed

- Resolves issue that breaks `OpenAQ.locations()` method and `AsyncOpenAQ.locations()` from upstream API change. Checks for and ignore fields not included in response model.

## [0.2.0] - 2023-12-21

### Added

- `parameters_id` arguments for `OpenAQ.locations()` method and `AsyncOpenAQ.locations()` method
- Added `Forbidden` and `ServerError` exceptions to `__all__` export.
- vendored pyhump, removed as `pyproject.toml` dependency

## [0.1.1] - 2023-10-31

### Fixed

- `AsyncOpenAQ` client `close()` method.

## [0.1.0] - 2023-10-31

Initial release


