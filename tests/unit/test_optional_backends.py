import importlib.util

from sematryx_engine.engine.strategy_selector import STRATEGIES
from sematryx_engine.solvers.non_scipy_solvers import available_optional_strategies


def test_optional_strategy_availability_matches_installed_packages() -> None:
    optional = set(available_optional_strategies())
    if importlib.util.find_spec("cma") is None:
        assert "cma_es" not in optional
    if importlib.util.find_spec("skopt") is None:
        assert "skopt_gp" not in optional
        assert "skopt_forest" not in optional
        assert "skopt_gbrt" not in optional


def test_selector_roster_contains_all_available_optionals() -> None:
    optional = set(available_optional_strategies())
    assert optional.issubset(set(STRATEGIES))
