from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, cast

VariableKind = Literal["continuous", "integer", "categorical"]


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
