# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [1.2.0] - unreleased

### Added

- Support for Python 3.15.
- CodSpeed benchmark suite (`tests/benchmarks/`) covering parsing
  (measurements, locations, sensors, latest) and serialization (`.json()` with
  stdlib/orjson, `.dict()`).

### Changed

- Annotated `OpenAQ.__enter__` and `Headers.copy` with `typing.Self` so type
  checkers infer the correct return type for subclasses. Also removed
  `from __future__ import annotations` from `client.py` and `transport.py`.
- Faster response parsing and serialization. `read_response()`, `.json()` and
  `.dict()` now do less work per call. Field-name mappings, header field names
  and each response class's result type are worked out once and cached, and
  nested data is no longer rebuilt in multiple times. The output of `.json()`
  and `.dict()` is unchanged.
- `.json()` now builds camelCase output in a single pass over the model
  instead of calling `.dict()` and then renaming keys in a second pass.
- `.dict()` no longer uses `dataclasses.asdict()`. It still uses snake_case
  field names and keeps the same field order and types as before.

### Removed

- Support for Python 3.10. The minimum supported version is now 3.11.
- Private `_ResponseBase._serialize()` method.

### Fixed

- Passing a time-zone-aware `datetime_from` without a `datetime_to` no longer
  raises `TypeError`.
- Passing one time-zone-aware and one naive datetime for `datetime_from` and
  `datetime_to` now raises a clear `InvalidParameterError` instead of a
  `TypeError`.

### Security

- Pinned `slackapi/slack-github-action` to a commit SHA and upgraded it from
  v2.0.0 to v4.0.0.
  
## [1.1.0] - 2026-07-02

### Added

- Additional check for valid API key in client instantiation.

### Changed

- Updated rate limiter to handle rare corner case caused by incorrect rounding
logic.

## [1.0.3] - 2026-06-19

No major changes bumping due to versioning issue in PyPI publishing.

## [1.0.2] - 2026-06-19

No major changes bumping due to versioning issue in PyPI publishing.

## [1.0.1] - 2026-06-19

No major changes bumping due to versioning issue in PyPI publishing.

## [1.0.0] - 2026-06-18

### Added

- orjson optional dependency extras group (`openaq[orjson]`)
- Additional test coverage

### Changed

- Rate limit wait behavior now enforces a minimum 1-second sleep when reset time
is zero or in the past, preventing races at the reset boundary.
- Headers rate limit fields changed from `int | None` defaulting to `None` to
`int` defaulting to 0.
- `orjson` encoder path in json() now correctly decodes `bytes` to `str`.
- Modernized type annotations throughout: `Mapping` and `Sequence` imports.
migrated from typing to `collections.abc`. `isinstance` checks updated to union
syntax `(X | Y)`. Headers typed as `dict[str, str]`; `_ResponseBase TypeVar`
bound tightened to `_ResponseBase[Any]`. `dict()` return type annotated as
`dict[str, Any]`.
- Replaced Black and isort with Ruff as sole code style and formatting tool
- Config file location moved from ~/.openaq.toml to ~/.config/openaq/config.toml.
- Replaced mkdocs documentation with Astro Starlight.

### Removed

- mkdocs.yml and MkDocs-based documentation infrastructure
- black, isort, and pydocstyle from style tooling dependencies

## [1.0.0rc3] - 2026-05-23

**Breaking changes**

### Removed

- Refactors Transport to no longer have HTTPX as dependency
- Removed AsyncClient, now only a synchronous OpenAQ client is exported

## [1.0.0rc2] - 2026-02-24

### Updated

- HTTPX client configuration settings for timeout
- HTTPX client configuration settings for limits

### Fixed

- Fixed creation of headers on client classes to remove mutable default argument.
- Fixed creation of transport on client classes to remove mutable default argument.
- automatic rate limiting for AsyncOpenAQ, no longer relies solely on HTTP
headers, a more reliable method for async usage.

## [1.0.0rc1] - 2026-02-13

**Breaking changes**

### Added

- `auto_wait` parameter for OpenAQ and AsyncOpenAQ to provide automatic waiting
based on rate limit headers
- New validation function to ensure `iso` and `countries_id` are not used
together
- New validation function to ensure `datetime_from` is always less than
`datetime_to`
- New validation function to ensure `date_to` is always less than
`date_to`
- New validation function to ensure `date_to`/`date_from` and
`datetime_from`/`datetime_to` are correctly paired with correct data resource.
- New validation function to ensure valid combinations of `data` and `rollup`

### Fixed

- Correctly pass `date_to` and `date_from` for `days` and `years` measurement
resources.
- Added missing arguments for `locations.list()` functions: `manufacturers_id`, 
`instruments_id` and the `owners_id`

### Updated

- `data` argument no longer defaults to `measurements` in measurements.list()
function, it is now a required argument.
- `datetime_from` no longer defaults in the library.

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


