import random

from sematryx_engine.learning.bandit import StrategyBandit


def test_stochastic_select_reports_posterior_mean_not_thompson_draw() -> None:
    random.seed(42)
    bandit = StrategyBandit(["a", "b"])
    for _ in range(30):
        bandit.update("a", 1.0)
    for _ in range(5):
        bandit.update("b", 0.0)
    name, confidence = bandit.select(["a", "b"], deterministic=False)
    assert name in ("a", "b")
    expected = bandit.posterior_mean(name)
    assert confidence == expected
    assert 0.0 < confidence < 1.0
