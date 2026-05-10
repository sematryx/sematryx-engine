import math

from sematryx_engine.api.variable_descriptors import (
    descriptor_learning_features,
    normalize_variable_descriptors,
)


def test_descriptor_learning_features_discrete_only_counts() -> None:
    desc = normalize_variable_descriptors(
        [
            {"kind": "integer", "low": 0, "high": 3},
            {"kind": "categorical", "categories": ["a", "b"]},
        ]
    )
    feat = descriptor_learning_features(desc)
    assert feat["descriptor_mix"] == "discrete_only"
    assert feat["n_continuous_variables"] == 0
    assert feat["n_integer_variables"] == 1
    assert feat["n_categorical_variables"] == 1
    assert math.isclose(
        float(feat["log_discrete_configuration_measure"]),
        math.log(4.0) + math.log(2.0),
    )


def test_descriptor_learning_features_mixed() -> None:
    desc = normalize_variable_descriptors(
        [
            {"kind": "continuous", "low": 0.0, "high": 1.0},
            {"kind": "integer", "low": 1, "high": 3},
        ]
    )
    feat = descriptor_learning_features(desc)
    assert feat["descriptor_mix"] == "mixed"
    assert feat["n_continuous_variables"] == 1
    assert feat["n_integer_variables"] == 1
    assert feat["n_categorical_variables"] == 0
    assert math.isclose(float(feat["log_discrete_configuration_measure"]), math.log(3.0))
