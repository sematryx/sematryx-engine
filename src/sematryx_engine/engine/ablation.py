"""Ablation configuration for measuring per-feature contribution.

`AblationConfig` toggles each integrated optimizer feature to a documented neutral fallback
(see ADR-0024). Production callers pass `None`; the harness passes explicit configs.
"""

from __future__ import annotations

from dataclasses import dataclass, fields, replace


@dataclass(frozen=True, slots=True)
class AblationConfig:
    """Independent on/off flags for each integrated optimizer feature.

    All-on (the value returned by ``default()``) is byte-identical to the pre-PRD-0025 call
    path; ``optimize(..., ablation=None)`` and ``optimize(..., ablation=AblationConfig.default())``
    must produce identical results for the same seeded inputs.
    """

    shape_routing: bool = True
    tuning_priors: bool = True
    autodidactic_loop: bool = True
    memory_override: bool = True
    descriptor_mix_memory: bool = True
    hybrid_outer_acquisition: bool = True
    hybrid_outer_refinement: bool = True
    continuous_bandit: bool = True

    @classmethod
    def default(cls) -> "AblationConfig":
        """All features on. The canonical production configuration."""
        return cls()

    @classmethod
    def all_off(cls) -> "AblationConfig":
        """All features off. Useful as a sanity reference, not a production path."""
        return cls(
            shape_routing=False,
            tuning_priors=False,
            autodidactic_loop=False,
            memory_override=False,
            descriptor_mix_memory=False,
            hybrid_outer_acquisition=False,
            hybrid_outer_refinement=False,
            continuous_bandit=False,
        )

    def with_off(self, knob: str) -> "AblationConfig":
        """Return a copy with one named knob disabled. Used by the harness matrix runner."""
        if knob not in KNOB_NAMES:
            raise ValueError(f"Unknown ablation knob: {knob!r}. Known: {sorted(KNOB_NAMES)}")
        return replace(self, **{knob: False})

    def is_default(self) -> bool:
        """True iff every knob is on (i.e. equal to ``AblationConfig.default()``)."""
        return all(getattr(self, f.name) for f in fields(self))


KNOB_NAMES: frozenset[str] = frozenset(f.name for f in fields(AblationConfig))


def coerce(ablation: AblationConfig | None) -> AblationConfig:
    """Resolve ``None`` to the all-on default. Used at every call site so branches read one
    object, never a nullable, and the byte-identity contract is mechanical."""
    return ablation if ablation is not None else AblationConfig.default()
