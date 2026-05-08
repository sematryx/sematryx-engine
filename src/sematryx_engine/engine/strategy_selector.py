from pathlib import Path

from sematryx_engine.engine.problem_features import ProblemFeatures
from sematryx_engine.learning.bandit import StrategyBandit
from sematryx_engine.learning.strategy_memory import LocalStrategyMemory

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
]


def memory_override_confidence(usage_count: int) -> float:
    """Confidence for deterministic domain-memory override from historical usage_count.

    Requires at least three stored runs before override applies; confidence rises with
    evidence and caps at 0.95.
    """
    if usage_count < 3:
        return 0.0
    return round(min(0.95, 0.72 + 0.06 * float(usage_count)), 10)


def _topology_tunneling_override(
    topology_artifact: dict[str, object] | None,
) -> tuple[str, float] | None:
    if not isinstance(topology_artifact, dict):
        return None
    raw_score = topology_artifact.get("physarum_tunneling_score", 0.0)
    if isinstance(raw_score, (int, float)):
        score = float(raw_score)
    else:
        score = 0.0
    directive = str(topology_artifact.get("tunneling_directive", ""))
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
        topology_artifact: dict[str, object] | None = None,
        deterministic_bandit: bool = False,
    ) -> tuple[str, float]:
        strategy, confidence, _basis = self.select_with_basis(
            features=features,
            domain=domain,
            topology_artifact=topology_artifact,
            deterministic_bandit=deterministic_bandit,
        )
        return strategy, confidence

    def select_with_basis(
        self,
        *,
        features: ProblemFeatures,
        domain: str,
        topology_artifact: dict[str, object] | None = None,
        deterministic_bandit: bool = False,
    ) -> tuple[str, float, str]:
        # Keep strategy filtering deterministic and simple in v1.
        if features.dimensions > 12:
            candidates = ["scipy_de", "scipy_dual_annealing", "scipy_shgo"]
        elif features.complexity == "low":
            candidates = ["scipy_local_lbfgsb", "scipy_local_powell", "scipy_de"]
        else:
            candidates = list(STRATEGIES)

        # Domain recommendations can override cold-start when evidence is strong.
        recommendations = self._memory.get_strategy_recommendations(domain=domain, limit=2)
        if recommendations:
            top = recommendations[0]
            # Use deterministic memory override only with enough historical evidence.
            if top.usage_count >= 3:
                return top.strategy_name, memory_override_confidence(top.usage_count), "memory_override"

        tunneling_choice = _topology_tunneling_override(topology_artifact)
        if tunneling_choice is not None:
            strategy, confidence = tunneling_choice
            return strategy, confidence, "physarum_tunneling_override"

        for rec in recommendations:
            if rec.strategy_name in STRATEGIES and rec.strategy_name not in candidates:
                candidates.append(rec.strategy_name)

        strategy, confidence = self._bandit.select(candidates, deterministic=deterministic_bandit)
        return strategy, confidence, "bandit"

    def update(self, strategy_name: str, reward: float) -> None:
        self._bandit.update(strategy_name, reward)
