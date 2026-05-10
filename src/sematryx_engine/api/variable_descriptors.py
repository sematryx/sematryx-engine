from __future__ import annotations

import math
from dataclasses import dataclass
from collections.abc import Sequence
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


def descriptor_learning_features(descriptors: list[VariableDescriptor]) -> dict[str, object]:
    """Stable JSON-friendly features for memory/analytics on typed-variable runs."""
    mix = classify_descriptor_mix(descriptors)
    n_continuous = sum(1 for d in descriptors if d.kind == "continuous")
    n_integer = sum(1 for d in descriptors if d.kind == "integer")
    n_categorical = sum(1 for d in descriptors if d.kind == "categorical")
    log_measure = 0.0
    for desc in descriptors:
        if desc.kind == "integer":
            assert desc.low is not None and desc.high is not None
            lo = math.ceil(float(desc.low))
            hi = math.floor(float(desc.high))
            span = max(1, hi - lo + 1)
            log_measure += math.log(float(span))
        elif desc.kind == "categorical":
            n = len(desc.categories)
            log_measure += math.log(float(max(1, n)))
    return {
        "descriptor_mix": mix,
        "n_continuous_variables": n_continuous,
        "n_integer_variables": n_integer,
        "n_categorical_variables": n_categorical,
        "log_discrete_configuration_measure": log_measure,
    }


def classify_descriptor_mix(descriptors: list[VariableDescriptor]) -> DescriptorMix:
    kinds = {d.kind for d in descriptors}
    has_continuous = "continuous" in kinds
    has_discrete = "integer" in kinds or "categorical" in kinds
    if has_continuous and has_discrete:
        return "mixed"
    if has_continuous:
        return "continuous_only"
    return "discrete_only"


def descriptors_to_mixed_encoded_bounds(
    descriptors: list[VariableDescriptor],
) -> list[tuple[float, float]]:
    """Full bound tuple per variable in descriptor order (mixed continuous/discrete)."""
    bounds: list[tuple[float, float]] = []
    for desc in descriptors:
        if desc.kind == "continuous":
            assert desc.low is not None and desc.high is not None
            bounds.append((desc.low, desc.high))
        elif desc.kind == "integer":
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
            raise AssertionError("unreachable")
    return bounds


def normalize_mixed_solution(x: Sequence[float], descriptors: list[VariableDescriptor]) -> list[float]:
    """Clamp/normalize each dimension to valid encoded values."""
    out: list[float] = []
    for xi, desc in zip(x, descriptors, strict=True):
        if desc.kind == "continuous":
            assert desc.low is not None and desc.high is not None
            v = float(xi)
            out.append(max(desc.low, min(desc.high, v)))
        elif desc.kind == "integer":
            assert desc.low is not None and desc.high is not None
            lo = math.ceil(float(desc.low))
            hi = math.floor(float(desc.high))
            v = int(round(float(xi)))
            v = max(lo, min(hi, v))
            out.append(float(v))
        elif desc.kind == "categorical":
            n = len(desc.categories)
            v = int(round(float(xi)))
            v = max(0, min(n - 1, v))
            out.append(float(v))
        else:
            raise AssertionError("unreachable")
    return out


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
                "continuous_only bounds conversion requires all descriptors to be continuous; "
                "use discrete-only or mixed routing for other kinds."
            )
        assert desc.low is not None and desc.high is not None
        bounds.append((desc.low, desc.high))
    return bounds
