from sematryx_engine.engine.problem_features import ProblemFeatures
from sematryx_engine.learning.bandit import StrategyBandit
from sematryx_engine.learning.strategy_memory import LocalStrategyMemory

STRATEGIES = [
    "scipy_de",
    "scipy_dual_annealing",
    "scipy_local_lbfgsb",
]


class StrategySelector:
    def __init__(self, memory: LocalStrategyMemory) -> None:
        self._bandit = StrategyBandit(STRATEGIES)
        self._memory = memory

    def select(self, features: ProblemFeatures, domain: str) -> tuple[str, float]:
        # Keep strategy filtering deterministic and simple in v1.
        if features.dimensions > 12:
            candidates = ["scipy_de", "scipy_dual_annealing"]
        elif features.complexity == "low":
            candidates = ["scipy_local_lbfgsb", "scipy_de"]
        else:
            candidates = list(STRATEGIES)

        # Domain recommendations influence candidate order but stay non-blocking.
        recommendations = self._memory.get_strategy_recommendations(domain=domain, limit=2)
        for rec in recommendations:
            if rec.strategy_name in STRATEGIES and rec.strategy_name not in candidates:
                candidates.append(rec.strategy_name)

        return self._bandit.select(candidates)

    def update(self, strategy_name: str, reward: float) -> None:
        self._bandit.update(strategy_name, reward)
