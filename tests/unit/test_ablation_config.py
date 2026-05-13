"""Unit tests for AblationConfig and the neutral tuning-priors fallback."""

from __future__ import annotations

import pytest

from sematryx_engine.engine.ablation import KNOB_NAMES, AblationConfig, coerce
from sematryx_engine.engine.tuning_priors import (
    compute_solver_tuning_priors,
    neutral_tuning_priors,
)
from sematryx_engine.engine.problem_features import extract_problem_features


def test_default_config_is_all_on() -> None:
    cfg = AblationConfig.default()
    assert cfg.is_default()
    assert cfg.shape_routing
    assert cfg.tuning_priors
    assert cfg.autodidactic_loop
    assert cfg.memory_override
    assert cfg.descriptor_mix_memory
    assert cfg.hybrid_outer_acquisition
    assert cfg.hybrid_outer_refinement
    assert cfg.continuous_bandit


def test_all_off_config_disables_every_knob() -> None:
    cfg = AblationConfig.all_off()
    for knob in KNOB_NAMES:
        assert getattr(cfg, knob) is False, knob
    assert not cfg.is_default()


def test_knob_names_cover_every_field() -> None:
    expected = {
        "shape_routing",
        "tuning_priors",
        "autodidactic_loop",
        "memory_override",
        "descriptor_mix_memory",
        "hybrid_outer_acquisition",
        "hybrid_outer_refinement",
        "continuous_bandit",
    }
    assert KNOB_NAMES == expected


def test_with_off_disables_only_named_knob() -> None:
    cfg = AblationConfig.default().with_off("shape_routing")
    assert cfg.shape_routing is False
    # Every other knob remains on.
    for knob in KNOB_NAMES - {"shape_routing"}:
        assert getattr(cfg, knob) is True, knob


def test_with_off_rejects_unknown_knob() -> None:
    with pytest.raises(ValueError, match="Unknown ablation knob"):
        AblationConfig.default().with_off("not_a_real_knob")


def test_coerce_none_returns_default() -> None:
    coerced = coerce(None)
    assert coerced == AblationConfig.default()
    assert coerced.is_default()


def test_coerce_passes_through_existing_config() -> None:
    cfg = AblationConfig(shape_routing=False)
    assert coerce(cfg) is cfg


def test_config_is_frozen() -> None:
    cfg = AblationConfig.default()
    with pytest.raises(Exception):
        cfg.shape_routing = False  # type: ignore[misc]


def test_neutral_priors_have_pinned_schema() -> None:
    priors = neutral_tuning_priors()
    assert priors == {
        "version": 1,
        "budget_multiplier": 1.0,
        "de_polish": True,
        "de_population_scale": 1.0,
        "dual_annealing_restart_temp_ratio": 2e-5,
        "shgo_sampling_scale": 1.0,
    }


def test_neutral_priors_share_keys_with_computed_priors() -> None:
    """The two priors paths must be drop-in compatible — same keys, same value types."""
    computed = compute_solver_tuning_priors(
        features=extract_problem_features(
            bounds=[(-1.0, 1.0), (-2.0, 2.0)],
            max_evaluations=200,
        ),
        budget_regime="moderate",
        shape_routing_directive="balanced",
        domain="general",
    )
    neutral = neutral_tuning_priors()
    assert set(computed.keys()) == set(neutral.keys())
    for key in computed:
        assert type(computed[key]) is type(neutral[key]), key
