# Ablation matrix report

Generated: `2026-05-12T23:14:06Z`  
Mode: `heavy` (seeds N=100)  
Git rev: `bc5a1a5`

Verdict rule (ADR-0024 §3): direction + significance only. `feature helps` = median worsens when off, p < 0.05. `regression` = median improves when off, p < 0.05. `no effect` = p ≥ 0.05.

## `sphere_smooth`

All-on baseline: median = `0`  success = `1.00`  mean evals = `20.6`

| Knob off | Knob-off median | Δ median | p-value | Verdict |
|----------|----------------|----------|---------|---------|
| `autodidactic_loop` | `0` | `+0.00%` | `0.028` | **no effect** |
| `continuous_bandit` | `0` | `+0.00%` | `0.264` | **no effect** |
| `descriptor_mix_memory` | `0` | `+0.00%` | `1.000` | **no effect** |
| `hybrid_outer_acquisition` | `0` | `+0.00%` | `1.000` | **no effect** |
| `hybrid_outer_refinement` | `0` | `+0.00%` | `1.000` | **no effect** |
| `memory_override` | `0` | `+0.00%` | `1.000` | **no effect** |
| `topology_routing` | `0` | `+0.00%` | `1.000` | **no effect** |
| `tuning_priors` | `0` | `+0.00%` | `0.901` | **no effect** |

## `rugged_multimodal_8d`

All-on baseline: median = `0.471345`  success = `1.00`  mean evals = `2622.2`

| Knob off | Knob-off median | Δ median | p-value | Verdict |
|----------|----------------|----------|---------|---------|
| `autodidactic_loop` | `0.943802` | `+100.24%` | `0.000` | **feature helps** |
| `continuous_bandit` | `0.471345` | `+0.00%` | `0.595` | **no effect** |
| `descriptor_mix_memory` | `0.471345` | `+0.00%` | `1.000` | **no effect** |
| `hybrid_outer_acquisition` | `0.471345` | `+0.00%` | `1.000` | **no effect** |
| `hybrid_outer_refinement` | `0.471345` | `+0.00%` | `1.000` | **no effect** |
| `memory_override` | `0.471345` | `+0.00%` | `1.000` | **no effect** |
| `topology_routing` | `0.471345` | `+0.00%` | `1.000` | **no effect** |
| `tuning_priors` | `0.705684` | `+49.72%` | `0.000` | **feature helps** |

## `discrete_knapsack`

All-on baseline: median = `0`  success = `1.00`  mean evals = `122.3`

| Knob off | Knob-off median | Δ median | p-value | Verdict |
|----------|----------------|----------|---------|---------|
| `autodidactic_loop` | `0` | `+0.00%` | `1.000` | **no effect** |
| `continuous_bandit` | `0` | `+0.00%` | `1.000` | **no effect** |
| `descriptor_mix_memory` | `0` | `+0.00%` | `1.000` | **no effect** |
| `hybrid_outer_acquisition` | `0` | `+0.00%` | `1.000` | **no effect** |
| `hybrid_outer_refinement` | `0` | `+0.00%` | `1.000` | **no effect** |
| `memory_override` | `0` | `+0.00%` | `1.000` | **no effect** |
| `topology_routing` | `0` | `+0.00%` | `1.000` | **no effect** |
| `tuning_priors` | `0` | `+0.00%` | `1.000` | **no effect** |

## `hybrid_mixed`

All-on baseline: median = `1`  success = `1.00`  mean evals = `470.8`

| Knob off | Knob-off median | Δ median | p-value | Verdict |
|----------|----------------|----------|---------|---------|
| `autodidactic_loop` | `1` | `+0.00%` | `1.000` | **no effect** |
| `continuous_bandit` | `1` | `+0.00%` | `0.913` | **no effect** |
| `descriptor_mix_memory` | `1` | `+0.00%` | `1.000` | **no effect** |
| `hybrid_outer_acquisition` | `1` | `+0.00%` | `0.918` | **no effect** |
| `hybrid_outer_refinement` | `1` | `+0.00%` | `1.000` | **no effect** |
| `memory_override` | `1` | `+0.00%` | `1.000` | **no effect** |
| `topology_routing` | `1` | `+0.00%` | `1.000` | **no effect** |
| `tuning_priors` | `1` | `+0.00%` | `0.922` | **no effect** |

