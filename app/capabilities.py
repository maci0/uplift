"""
Maturity model capabilities data.
Loaded from the original YAML and structured as Python dicts for direct use.
"""

import functools

import yaml
from pathlib import Path

from app.models.score import CATEGORY_FIELDS

_DATA_DIR = Path(__file__).parent.parent / "data"

_CATEGORY_NAMES = {
    "a": "Code",
    "b": "Build and Test",
    "c": "Release",
    "d": "Operate",
    "e": "Optimize",
}


@functools.cache
def _load_yaml(filename: str) -> dict:
    with open(_DATA_DIR / filename) as f:
        return yaml.safe_load(f)


def load_capabilities() -> dict:
    return _load_yaml("capabilities.yaml")


def load_formatted_capabilities() -> dict:
    return _load_yaml("formatted_capabilities.yaml")


# Category metadata — derived from the canonical field definitions in score.py
CATEGORIES = [
    {"key": key, "name": _CATEGORY_NAMES[key], "fields": fields}
    for key, fields in CATEGORY_FIELDS.items()
]


def get_capability_labels(capabilities: dict) -> list[str]:
    """Return ordered list of all 42 capability titles."""
    labels = []
    for cat in CATEGORIES:
        for field in cat["fields"]:
            labels.append(capabilities.get(field, field))
    return labels
