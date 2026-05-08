"""Public package API for sematryx-engine."""

from sematryx_engine.api.client import optimize
from sematryx_engine.api.explanation_formatter import (
    format_explanation_concise,
    format_explanation_verbose,
)
from sematryx_engine.api.models import OptimizationResult
from sematryx_engine.api.variable_descriptors import VariableDescriptor

__all__ = [
    "optimize",
    "OptimizationResult",
    "VariableDescriptor",
    "format_explanation_concise",
    "format_explanation_verbose",
]
