# OpenAQ Python SDK

The official Python SDK for the OpenAQ API.

> :warning: OpenAQ python is still under active development and may be unstable until a v1.0.0 release

[![PyPI - Version](https://img.shields.io/pypi/v/openaq.svg)](https://pypi.org/project/openaq)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/openaq.svg)](https://pypi.org/project/openaq)
![Codecov](https://img.shields.io/codecov/c/github/openaq/openaq-python)
![Static Badge](https://img.shields.io/badge/type%20checked-mypy-039dfc)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![slack](https://img.shields.io/badge/Slack-OpenAQ-blue?logo=slack&color=%23198cff
)](https://join.slack.com/t/openaq/shared_invite/zt-yzqlgsva-v6McumTjy2BZnegIK9XCVw)

-----

## Table of Contents

- [Installation](#installation)
- [Documentation](#documentation)
- [License](#license)

## Installation

OpenAQ python is availble on pip.

```console
pip install openaq
```

## Documentation

Documentation available at [python.openaq.org](https://python.openaq.org)

Documentation can also be run locally using `hatch run docs:serve`

## License

The OpenAQ Python SDK is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.

## Development

Code is styled according to [black](https://github.com/psf/black), imports are sorted using [isort](https://pycqa.github.io/isort/), and code is linted using [ruff](https://github.com/astral-sh/ruff).

Codebase can be automatically formatted and linted by running:

```console
hatch run style:fmt
```

style can be checked with:

```console
hatch run style:check
```

[mypy](https://mypy-lang.org/) static type checking:

```console
hatch run types:check
```

Testing uses [pytest](https://docs.pytest.org/en/7.4.x/).

```console
hatch run test:test
```

## Acknowledgements

For many years [py-openaq](https://github.com/dhhagan/py-openaq) by David Hagan filled the gap for a Python API SDK for the OpenAQ API. Thank you to David for many years of maintaining py-openaq and for taking the original step to develop a Python tool for OpenAQ.
