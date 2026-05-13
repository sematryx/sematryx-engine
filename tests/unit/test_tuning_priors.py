from sematryx_engine.engine.problem_features import ProblemFeatures
from sematryx_engine.engine.tuning_priors import (
    compute_solver_tuning_priors,
    domain_budget_anchor,
)


def test_domain_budget_anchor_is_stable_per_label() -> None:
    assert domain_budget_anchor("finance_opt") == domain_budget_anchor("finance_opt")


def test_compute_solver_tuning_priors_schema() -> None:
    features = ProblemFeatures(
        dimensions=8,
        avg_range=4.0,
        bounded=True,
        budget_per_dimension=45.0,
        complexity="medium",
    )
    priors = compute_solver_tuning_priors(
        features=features,
        budget_regime="moderate",
        shape_routing_directive="balanced",
        domain="unit_test_domain",
    )
    assert priors["version"] == 1
    assert isinstance(priors["budget_multiplier"], float)
    assert isinstance(priors["de_polish"], bool)
    assert isinstance(priors["de_population_scale"], float)
    assert isinstance(priors["dual_annealing_restart_temp_ratio"], float)
    assert isinstance(priors["shgo_sampling_scale"], float)
