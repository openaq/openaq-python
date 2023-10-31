# openaq-python

The official Python wrapper for the OpenAQ API.

> :warning: OpenAQ python is still under active development and may be unstable until a v1.0.0 release


OpenAQ Python is a low-level API wrapper for the OpenAQ Version 3 API. 

[![PyPI - Version](https://img.shields.io/pypi/v/openaq.svg)](https://pypi.org/project/openaq)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/openaq.svg)](https://pypi.org/project/openaq)

-----

**Table of Contents**

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

## License

`openaq` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.

## Development

Code is styled according to [black](https://github.com/psf/black), imports are sorted using [isort](https://pycqa.github.io/isort/) and code is linted using [ruff](https://github.com/astral-sh/ruff).

Codebase can be automatcally formatted and linted by running:

```console
hatch run style:fmt
```

style can be checked with:

```console
hatch run style:check
```

Testing uses [pytest](https://docs.pytest.org/en/7.4.x/).

```console
hatch run test:test
```

Code coverage can be viewed with:

```console
hatch run test:cov
```


## Acknowledgements

For many years [py-openaq](https://github.com/dhhagan/py-openaq) by David Hagan filled the gap for a Python API wrapper for the OpenAQ API. Thank you to David for many years of maintaining py-openaq and for taking the original step to develop a wrapper for OpenAQ.