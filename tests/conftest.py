import json
from functools import cache
from pathlib import Path

import pytest

@cache
def _read_json(path: Path) -> dict:
    return json.loads(path.read_text())

@pytest.fixture(scope="session")
def load_resource():
    return lambda name: _read_json(Path(__file__).parent / "fixtures" / "resources" / f"{name}.json")

@pytest.fixture(scope="session")
def load_response():
    return lambda name: _read_json(Path(__file__).parent / "fixtures" / "responses" / f"{name}.json")
