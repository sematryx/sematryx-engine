import math
import random

from sematryx_engine.api.variable_descriptors import VariableDescriptor
from sematryx_engine.solvers.discrete_solvers import (
    normalize_discrete_solution,
    solve_discrete_baseline,
)


def test_normalize_discrete_solution_integer_clamp() -> None:
    desc = [
        VariableDescriptor(kind="integer", low=0.0, high=5.0),
    ]
    assert normalize_discrete_solution([99.0], desc) == [5.0]
    assert normalize_discrete_solution([-1.0], desc) == [0.0]


def test_solve_discrete_baseline_deterministic_sphere() -> None:
    descriptors = [
        VariableDescriptor(kind="integer", low=-2.0, high=8.0),
        VariableDescriptor(kind="integer", low=-2.0, high=8.0),
    ]

    def obj(x: list[float]) -> float:
        return sum((v - 3.0) ** 2 for v in x)

    rng = random.Random(42)
    out = solve_discrete_baseline(obj, descriptors, max_evaluations=800, rng=rng)
    assert out.success is True
    assert out.nfev <= 800
    assert math.isclose(out.fun, 0.0, abs_tol=1e-9)
    assert all(abs(v - 3.0) < 1e-9 for v in out.x)
