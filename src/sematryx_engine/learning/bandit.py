import json
import random
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class ArmState:
    alpha: float = 1.0
    beta: float = 1.0


class StrategyBandit:
    """Simple Thompson-sampling bandit for solver strategies."""

    def __init__(self, strategy_names: list[str], state_path: Path | None = None) -> None:
        self._arms = {name: ArmState() for name in strategy_names}
        self._state_path = state_path
        if self._state_path is not None:
            self.load(self._state_path)

    def select(self, candidate_names: list[str], deterministic: bool = False) -> tuple[str, float]:
        if deterministic:
            means = [(name, self.posterior_mean(name)) for name in candidate_names]
            return max(means, key=lambda item: item[1])

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
        if self._state_path is not None:
            self.save(self._state_path)

    def posterior_mean(self, strategy_name: str) -> float:
        state = self._arms[strategy_name]
        return state.alpha / (state.alpha + state.beta)

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "arms": {
                name: {"alpha": state.alpha, "beta": state.beta}
                for name, state in self._arms.items()
            }
        }
        path.write_text(json.dumps(payload), encoding="utf-8")

    def load(self, path: Path) -> None:
        if not path.exists():
            return
        payload = json.loads(path.read_text(encoding="utf-8"))
        arms = payload.get("arms", {})
        for name, values in arms.items():
            if name not in self._arms:
                continue
            alpha = float(values.get("alpha", 1.0))
            beta = float(values.get("beta", 1.0))
            self._arms[name] = ArmState(alpha=alpha, beta=beta)
