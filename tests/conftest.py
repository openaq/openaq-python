"""Shared fixtures for all test suites."""

import json
from functools import cache
from pathlib import Path
from typing import Any

import pytest

FIXTURES = Path(__file__).parent / "fixtures"
RESOURCES = FIXTURES / "resources"
RESPONSES = FIXTURES / "responses"


@cache
def _read_json(path: Path) -> Any:
    return json.loads(path.read_text())


@pytest.fixture(scope="session")
def load_resource():
    return lambda name: _read_json(RESOURCES / f"{name}.json")


@pytest.fixture(scope="session")
def load_response():
    return lambda name: _read_json(RESPONSES / f"{name}.json")
