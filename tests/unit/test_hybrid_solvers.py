from sematryx_engine.api.variable_descriptors import VariableDescriptor
from sematryx_engine.solvers.hybrid_solvers import (
    continuous_bounds_only,
    discrete_descriptors_only,
    merge_mixed_solution,
)


def test_merge_and_splits_align_descriptor_order() -> None:
    descriptors = [
        VariableDescriptor(kind="continuous", low=0.0, high=1.0),
        VariableDescriptor(kind="integer", low=0.0, high=5.0),
        VariableDescriptor(kind="categorical", categories=("a", "b")),
    ]
    assert continuous_bounds_only(descriptors) == [(0.0, 1.0)]
    assert len(discrete_descriptors_only(descriptors)) == 2
    full = merge_mixed_solution(descriptors, [0.25], [3.0, 1.0])
    assert full == [0.25, 3.0, 1.0]
