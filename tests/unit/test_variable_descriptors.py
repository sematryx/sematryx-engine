import pytest

from sematryx_engine.api.variable_descriptors import (
    descriptors_to_bounds,
    normalize_variable_descriptors,
)


def test_normalize_continuous_descriptor() -> None:
    descriptors = normalize_variable_descriptors([{"kind": "continuous", "low": -2.0, "high": 2.0}])
    assert descriptors_to_bounds(descriptors) == [(-2.0, 2.0)]


def test_integer_descriptor_rejected_in_stage3_kickoff() -> None:
    descriptors = normalize_variable_descriptors([{"kind": "integer", "low": 0, "high": 5}])
    with pytest.raises(ValueError):
        descriptors_to_bounds(descriptors)


def test_categorical_descriptor_requires_categories() -> None:
    with pytest.raises(ValueError):
        normalize_variable_descriptors([{"kind": "categorical", "categories": []}])
