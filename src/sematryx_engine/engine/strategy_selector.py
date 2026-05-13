import random
from pathlib import Path

from sematryx_engine.engine.ablation import AblationConfig, coerce
from sematryx_engine.engine.problem_features import ProblemFeatures
from sematryx_engine.learning.bandit import StrategyBandit
from sematryx_engine.learning.strategy_memory import LocalStrategyMemory
from sematryx_engine.solvers.non_scipy_solvers import available_optional_strategies

STRATEGIES = [
    "scipy_de",
    "scipy_dual_annealing",
    "scipy_local_lbfgsb",
    "scipy_local_powell",
    "scipy_local_tnc",
    "scipy_local_slsqp",
    "scipy_local_cobyla",
    "scipy_local_nelder_mead",
    "scipy_local_cg",
    "scipy_shgo",
    "discrete_random_neighborhood",
    "hybrid_outer_random_inner_scipy",
] + available_optional_strategies()


def memory_override_confidence(usage_count: int) -> float:
    """Confidence for deterministic domain-memory override from historical usage_count.

    Requires at least three stored runs before override applies; confidence rises with
    evidence and caps at 0.95.
    """
    if usage_count < 3:
        return 0.0
    return round(min(0.95, 0.72 + 0.06 * float(usage_count)), 10)


def _shape_routing_override(
    problem_shape: dict[str, object] | None,
) -> tuple[str, float] | None:
    """Hardcoded routing override fired when the problem-shape classifier's score
    crosses 0.75 or its directive is ``aggressive``. Forces ``scipy_dual_annealing``.

    This is the legacy stub: it routes based on a problem-shape classifier, not on any
    landscape-topology analysis. See ADR-0026 for why the original Physarum→tunneling
    intent never landed and is now the substance of Stage 4 Slice 1.
    """
    if not isinstance(problem_shape, dict):
        return None
    raw_score = problem_shape.get("shape_routing_score", 0.0)
    if isinstance(raw_score, (int, float)):
        score = float(raw_score)
    else:
        score = 0.0
    directive = str(problem_shape.get("shape_routing_directive", ""))
    if directive == "aggressive" or score >= 0.75:
        return "scipy_dual_annealing", 0.86
    return None


class StrategySelector:
    def __init__(
        self,
        memory: LocalStrategyMemory,
        bandit_state_path: Path | None = None,
    ) -> None:
        self._bandit = StrategyBandit(STRATEGIES, state_path=bandit_state_path)
        self._memory = memory

    def select(
        self,
        features: ProblemFeatures,
        domain: str,
        problem_shape: dict[str, object] | None = None,
        deterministic_bandit: bool = False,
        *,
        memory_descriptor_mix: str | None = None,
        ablation: AblationConfig | None = None,
    ) -> tuple[str, float]:
        strategy, confidence, _basis = self.select_with_basis(
            features=features,
            domain=domain,
            problem_shape=problem_shape,
            deterministic_bandit=deterministic_bandit,
            memory_descriptor_mix=memory_descriptor_mix,
            ablation=ablation,
        )
        return strategy, confidence

    def select_with_basis(
        self,
        *,
        features: ProblemFeatures,
        domain: str,
        problem_shape: dict[str, object] | None = None,
        deterministic_bandit: bool = False,
        exclude_strategies: frozenset[str] | None = None,
        memory_descriptor_mix: str | None = None,
        ablation: AblationConfig | None = None,
    ) -> tuple[str, float, str]:
        ab = coerce(ablation)
        excluded = exclude_strategies or frozenset()
        # Keep strategy filtering deterministic and simple in v1.
        if features.dimensions > 12:
            candidates = ["scipy_de", "scipy_dual_annealing", "scipy_shgo"]
        elif features.complexity == "low":
            candidates = ["scipy_local_lbfgsb", "scipy_local_powell", "scipy_de"]
        else:
            candidates = list(STRATEGIES)
        candidates = [c for c in candidates if c not in excluded]

        # Domain recommendations can override cold-start when evidence is strong.
        if ab.memory_override:
            recommendations = self._memory.get_strategy_recommendations(
                domain=domain,
                limit=2,
                descriptor_mix=memory_descriptor_mix if ab.descriptor_mix_memory else None,
            )
            if recommendations:
                top = recommendations[0]
                # Use deterministic memory override only with enough historical evidence.
                if top.usage_count >= 3 and top.strategy_name not in excluded:
                    return top.strategy_name, memory_override_confidence(top.usage_count), "memory_override"
        else:
            recommendations = []

        if ab.shape_routing:
            routing_choice = _shape_routing_override(problem_shape)
            if routing_choice is not None:
                strategy, confidence = routing_choice
                if strategy not in excluded:
                    return strategy, confidence, "shape_routing_override"

        for rec in recommendations:
            if (
                rec.strategy_name in STRATEGIES
                and rec.strategy_name not in candidates
                and rec.strategy_name not in excluded
            ):
                candidates.append(rec.strategy_name)

        if not candidates:
            candidates = ["scipy_de"]

        if ab.continuous_bandit:
            strategy, confidence = self._bandit.select(candidates, deterministic=deterministic_bandit)
            return strategy, confidence, "bandit"
        chosen = random.choice(sorted(candidates))
        return chosen, 0.5, "uniform_random_strategy"

    def update(self, strategy_name: str, reward: float) -> None:
        self._bandit.update(strategy_name, reward)
