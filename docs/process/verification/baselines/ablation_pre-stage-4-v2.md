# Ablation matrix report

Generated: `2026-05-13T03:05:19Z`  
Mode: `heavy` (seeds N=100)  
Git rev: `1ecbcec`

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

All-on baseline: median = `0.471345`  success = `1.00`  mean evals = `2088.9`

| Knob off | Knob-off median | Δ median | p-value | Verdict |
|----------|----------------|----------|---------|---------|
| `autodidactic_loop` | `0.698123` | `+48.11%` | `0.000` | **feature helps** |
| `continuous_bandit` | `0.471345` | `+0.00%` | `0.473` | **no effect** |
| `descriptor_mix_memory` | `0.471345` | `+0.00%` | `1.000` | **no effect** |
| `hybrid_outer_acquisition` | `0.471345` | `+0.00%` | `1.000` | **no effect** |
| `hybrid_outer_refinement` | `0.471345` | `+0.00%` | `1.000` | **no effect** |
| `memory_override` | `0.471345` | `+0.00%` | `0.000` | **no effect** |
| `topology_routing` | `0.471345` | `+0.00%` | `1.000` | **no effect** |
| `tuning_priors` | `0.698123` | `+48.11%` | `0.000` | **feature helps** |

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

## `hybrid_separating`

All-on baseline: median = `2.46519e-32`  success = `1.00`  mean evals = `445.4`

| Knob off | Knob-off median | Δ median | p-value | Verdict |
|----------|----------------|----------|---------|---------|
| `autodidactic_loop` | `2.46519e-32` | `+0.00%` | `1.000` | **no effect** |
| `continuous_bandit` | `2.46519e-32` | `+0.00%` | `0.577` | **no effect** |
| `descriptor_mix_memory` | `2.46519e-32` | `+0.00%` | `1.000` | **no effect** |
| `hybrid_outer_acquisition` | `2.46519e-32` | `+0.00%` | `0.920` | **no effect** |
| `hybrid_outer_refinement` | `4` | `+16225927682921336339157801028812800.00%` | `0.000` | **feature helps** |
| `memory_override` | `2.46519e-32` | `+0.00%` | `1.000` | **no effect** |
| `topology_routing` | `2.46519e-32` | `+0.00%` | `1.000` | **no effect** |
| `tuning_priors` | `2.46519e-32` | `+0.00%` | `0.955` | **no effect** |

## `topology_firing_current`

All-on baseline: median = `0.951111`  success = `1.00`  mean evals = `563.0`

| Knob off | Knob-off median | Δ median | p-value | Verdict |
|----------|----------------|----------|---------|---------|
| `autodidactic_loop` | `0.951111` | `+0.00%` | `1.000` | **no effect** |
| `continuous_bandit` | `0.951111` | `+0.00%` | `1.000` | **no effect** |
| `descriptor_mix_memory` | `0.951111` | `+0.00%` | `1.000` | **no effect** |
| `hybrid_outer_acquisition` | `0.951111` | `+0.00%` | `1.000` | **no effect** |
| `hybrid_outer_refinement` | `0.951111` | `+0.00%` | `1.000` | **no effect** |
| `memory_override` | `0.951111` | `+0.00%` | `1.000` | **no effect** |
| `topology_routing` | `1.62819` | `+71.19%` | `0.000` | **feature helps** |
| `tuning_priors` | `0.951111` | `+0.00%` | `1.000` | **no effect** |

