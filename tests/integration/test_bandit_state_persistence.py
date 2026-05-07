from pathlib import Path

from sematryx_engine.engine.problem_features import extract_problem_features
from sematryx_engine.engine.strategy_selector import StrategySelector
from sematryx_engine.learning.strategy_memory import LocalStrategyMemory


def test_bandit_state_persists_across_selector_instances(tmp_path: Path) -> None:
    state_path = tmp_path / "bandit_state.json"
    memory = LocalStrategyMemory(tmp_path / "strategy_memory.db")
    selector = StrategySelector(memory=memory, bandit_state_path=state_path)

    for _ in range(20):
        selector.update("scipy_local_lbfgsb", 1.0)
    for _ in range(5):
        selector.update("scipy_de", 0.0)

    reloaded_selector = StrategySelector(memory=memory, bandit_state_path=state_path)
    features = extract_problem_features(
        bounds=[(-5.0, 5.0)] * 7,
        max_evaluations=200,
    )
    strategy, confidence = reloaded_selector.select(
        features=features,
        domain="general",
        deterministic_bandit=True,
    )

    assert strategy == "scipy_local_lbfgsb"
    assert confidence > 0.6
