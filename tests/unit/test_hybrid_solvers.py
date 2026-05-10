import random

from sematryx_engine.api.variable_descriptors import VariableDescriptor
from sematryx_engine.solvers.discrete_solvers import discrete_coordinate_neighbors
from sematryx_engine.solvers.hybrid_solvers import (
    continuous_bounds_only,
    discrete_descriptors_only,
    merge_mixed_solution,
    solve_hybrid_outer_random_inner_scipy,
)


def test_discrete_coordinate_neighbors_integer() -> None:
    desc = [VariableDescriptor(kind="integer", low=0.0, high=2.0)]
    nbrs = discrete_coordinate_neighbors([1.0], desc, 0)
    values = {n[0] for n in nbrs}
    assert values == {0.0, 2.0}


def test_hybrid_outer_refinement_reaches_mixed_optimum() -> None:
    def narrow_shell(x: list[float]) -> float:
        return (x[0] - 0.5) ** 2 + (x[1] - 1.0) ** 2

    descriptors = [
        VariableDescriptor(kind="continuous", low=0.0, high=1.0),
        VariableDescriptor(kind="integer", low=0.0, high=2.0),
    ]
    result = solve_hybrid_outer_random_inner_scipy(
        narrow_shell,
        descriptors,
        400,
        inner_strategy="scipy_de",
        tuning_priors={},
        rng=random.Random(42),
    )
    assert result.message == "hybrid_outer_acquisition_lcb_inner_scipy_refined"
    assert result.success is True
    assert float(result.fun) < 0.05
    assert abs(result.x[0] - 0.5) < 0.15
    assert abs(result.x[1] - 1.0) < 0.51


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
