import random
from dataclasses import dataclass


@dataclass(slots=True)
class ArmState:
    alpha: float = 1.0
    beta: float = 1.0


class StrategyBandit:
    """Simple Thompson-sampling bandit for solver strategies."""

    def __init__(self, strategy_names: list[str]) -> None:
        self._arms = {name: ArmState() for name in strategy_names}

    def select(self, candidate_names: list[str]) -> tuple[str, float]:
        draws: list[tuple[str, float]] = []
        for name in candidate_names:
            state = self._arms[name]
            draws.append((name, random.betavariate(state.alpha, state.beta)))
        selected = max(draws, key=lambda item: item[1])
        return selected

    def update(self, strategy_name: str, reward: float) -> None:
        state = self._arms[strategy_name]
        clipped = max(0.0, min(1.0, reward))
        state.alpha += clipped
        state.beta += 1.0 - clipped
