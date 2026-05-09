from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Literal, cast

VariableKind = Literal["continuous", "integer", "categorical"]

DescriptorMix = Literal["continuous_only", "discrete_only", "mixed"]


@dataclass(frozen=True, slots=True)
class VariableDescriptor:
    kind: VariableKind
    low: float | None = None
    high: float | None = None
    categories: tuple[str, ...] = ()


def normalize_variable_descriptors(
    descriptors: list[dict[str, object]],
) -> list[VariableDescriptor]:
    normalized: list[VariableDescriptor] = []
    for row in descriptors:
        kind_obj = row.get("kind")
        if not isinstance(kind_obj, str):
            raise ValueError("Variable descriptor requires string 'kind'.")
        if kind_obj not in {"continuous", "integer", "categorical"}:
            raise ValueError(f"Unsupported variable kind: {kind_obj}")

        if kind_obj in {"continuous", "integer"}:
            low = row.get("low")
            high = row.get("high")
            if not isinstance(low, (int, float)) or not isinstance(high, (int, float)):
                raise ValueError(f"{kind_obj} variable requires numeric 'low' and 'high'.")
            if float(low) >= float(high):
                raise ValueError(f"{kind_obj} variable requires low < high.")
            normalized.append(
                VariableDescriptor(
                    kind=cast(VariableKind, kind_obj),
                    low=float(low),
                    high=float(high),
                )
            )
            continue

        categories_obj = row.get("categories")
        if not isinstance(categories_obj, list) or not categories_obj:
            raise ValueError("categorical variable requires non-empty 'categories' list.")
        categories: list[str] = []
        for val in categories_obj:
            if not isinstance(val, str) or not val:
                raise ValueError("categorical categories must be non-empty strings.")
            categories.append(val)
        normalized.append(VariableDescriptor(kind="categorical", categories=tuple(categories)))

    return normalized


def classify_descriptor_mix(descriptors: list[VariableDescriptor]) -> DescriptorMix:
    kinds = {d.kind for d in descriptors}
    has_continuous = "continuous" in kinds
    has_discrete = "integer" in kinds or "categorical" in kinds
    if has_continuous and has_discrete:
        return "mixed"
    if has_continuous:
        return "continuous_only"
    return "discrete_only"


def descriptors_to_encoded_bounds(descriptors: list[VariableDescriptor]) -> list[tuple[float, float]]:
    """Bounds over encoded vectors for topology/feature extraction (discrete-only problems)."""
    bounds: list[tuple[float, float]] = []
    for desc in descriptors:
        if desc.kind == "integer":
            assert desc.low is not None and desc.high is not None
            lo = float(math.ceil(float(desc.low)))
            hi = float(math.floor(float(desc.high)))
            if lo > hi:
                raise ValueError("integer variable has empty domain after rounding bounds.")
            bounds.append((lo, hi))
        elif desc.kind == "categorical":
            n = len(desc.categories)
            bounds.append((0.0, float(n - 1)))
        else:
            raise ValueError("descriptors_to_encoded_bounds expects discrete descriptors only.")
    return bounds


def descriptors_to_bounds(descriptors: list[VariableDescriptor]) -> list[tuple[float, float]]:
    bounds: list[tuple[float, float]] = []
    for desc in descriptors:
        if desc.kind != "continuous":
            raise ValueError(
                "Stage 3 kickoff supports descriptor validation only; integer/categorical solving "
                "lands in later Stage 3 slices."
            )
        assert desc.low is not None and desc.high is not None
        bounds.append((desc.low, desc.high))
    return bounds
