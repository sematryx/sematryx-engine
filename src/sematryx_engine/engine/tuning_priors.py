"""Deterministic solver hyperparameter priors from domain label and problem topology."""

from __future__ import annotations

from sematryx_engine.engine.problem_features import ProblemFeatures


def neutral_tuning_priors() -> dict[str, object]:
    """Topology- and domain-blind defaults used when the tuning-priors ablation is off.

    Matches the pre-feature historical behaviour: unit multipliers, polish enabled, the
    existing tight-regime restart ratio, and unit SHGO scale. Version pinned to the same
    schema as ``compute_solver_tuning_priors`` so downstream consumers do not branch.
    """
    return {
        "version": 1,
        "budget_multiplier": 1.0,
        "de_polish": True,
        "de_population_scale": 1.0,
        "dual_annealing_restart_temp_ratio": 2e-5,
        "shgo_sampling_scale": 1.0,
    }


def domain_budget_anchor(domain: str) -> float:
    """Stable multiplier in ``[0.93, 1.07]`` derived from the domain label."""
    if not domain.strip():
        return 1.0
    total = sum(ord(c) for c in domain)
    span = (total % 15) / 14.0
    return round(0.93 + span * 0.14, 6)


def compute_solver_tuning_priors(
    *,
    features: ProblemFeatures,
    topology_budget_regime: str,
    tunneling_directive: str,
    domain: str,
) -> dict[str, object]:
    """Return a versioned dict consumed by ``solve_with_scipy`` and explanations."""
    complexity_budget = {"low": 1.03, "medium": 1.0, "high": 0.97}
    topology_budget = {"generous": 1.05, "moderate": 1.0, "tight": 0.94}
    tunneling_population = {"local": 1.0, "balanced": 1.06, "aggressive": 1.12}

    cx = complexity_budget.get(features.complexity, 1.0)
    tb = topology_budget.get(topology_budget_regime, 1.0)
    anchor = domain_budget_anchor(domain)
    budget_multiplier = min(1.14, max(0.86, anchor * cx * tb))
    budget_multiplier = round(budget_multiplier, 6)

    polish = not (topology_budget_regime == "tight" and tunneling_directive == "aggressive")

    pop_scale = tunneling_population.get(tunneling_directive, 1.0)
    if features.dimensions > 12:
        pop_scale *= 0.93

    restart_ratio = {"tight": 2e-5, "moderate": 1.2e-5, "generous": 8e-6}.get(
        topology_budget_regime, 2e-5
    )

    shgo_scale = 1.0 + (0.1 if features.complexity == "high" else 0.0)
    if topology_budget_regime == "tight":
        shgo_scale *= 0.92

    return {
        "version": 1,
        "budget_multiplier": budget_multiplier,
        "de_polish": polish,
        "de_population_scale": round(pop_scale, 6),
        "dual_annealing_restart_temp_ratio": restart_ratio,
        "shgo_sampling_scale": round(shgo_scale, 6),
    }
