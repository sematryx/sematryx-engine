from collections.abc import Callable

from sematryx_engine.api.models import OptimizationResult
from sematryx_engine.api.variable_descriptors import (
    classify_descriptor_mix,
    descriptors_to_bounds,
    descriptors_to_encoded_bounds,
    normalize_variable_descriptors,
)
from sematryx_engine.engine.optimizer import run_optimization


def optimize(
    objective_function: Callable[[list[float]], float],
    bounds: list[tuple[float, float]] | None = None,
    *,
    variable_descriptors: list[dict[str, object]] | None = None,
    max_evaluations: int = 1000,
    domain: str = "general",
) -> OptimizationResult:
    if variable_descriptors is not None:
        descriptors = normalize_variable_descriptors(variable_descriptors)
        mix = classify_descriptor_mix(descriptors)
        if mix == "mixed":
            raise ValueError(
                "Mixed continuous and discrete variables are not supported until Stage 3 hybrid routing."
            )
        if mix == "discrete_only":
            return run_optimization(
                objective_function=objective_function,
                bounds=descriptors_to_encoded_bounds(descriptors),
                max_evaluations=max_evaluations,
                domain=domain,
                discrete_descriptors=descriptors,
            )
        effective_bounds = descriptors_to_bounds(descriptors)
    elif bounds is not None:
        effective_bounds = bounds
    else:
        raise ValueError("Either bounds or variable_descriptors must be provided.")

    return run_optimization(
        objective_function=objective_function,
        bounds=effective_bounds,
        max_evaluations=max_evaluations,
        domain=domain,
    )
