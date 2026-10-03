# 013 — Reviewer-hardening robustness campaign

## Purpose

This experiment addresses reviewer-sensitive modeling choices without modifying the frozen publication operating-envelope evidence.

## Scientific questions

1. Does the density/interference conclusion depend on deterministic sequential disjoint pairing?
2. Does the resource-separation benefit persist relative to a seeded random no-coordination allocator?
3. Does the qualitative conclusion depend on idealized expected-goodput-maximizing link adaptation?
4. Does the frozen nominal-channel PRB-share noise-bandwidth convention materially affect the result relative to exact occupied PRB bandwidth?

## Design

- swarm sizes: `N = [20, 50, 100]`
- resources: `R = [1, 4, 8]`
- directional relative advantage: `G = [0, 6] dB`
- pairings: `sequential`, `nearest_neighbor`
- allocators: `weighted conflict graph`, `seeded random` (R>1)
- link adaptation: `adaptive`, `fixed_mcs4`
- noise bandwidth: exact occupied OFDM bandwidth `N_PRB * 12 * 30 kHz`
- full run: 100 deterministic seeds

The same measured-A2A large-scale model, NR resource-grid mechanics, and official 5G-LENA v5.0 Table-1 BLER source are used.

## Interpretation

This is a sensitivity/robustness experiment, not a replacement canonical campaign. No result direction is assumed in advance. A manuscript claim may be added only after the committed workflow succeeds and the generated tables are audited.

## Expected outputs

- `results/paper_robustness/per_seed.csv`
- `results/paper_robustness/summary.csv`
- `results/paper_robustness/manifest.json`

## Publication rule

If robustness checks support the same qualitative conclusion, report that conclusion with the exact sensitivity dimensions tested. If a conclusion changes materially, revise the paper claim rather than hiding the sensitivity.

## Completed evidence

The full 100-seed robustness campaign completed successfully on:

- scientific commit: `f224ba9e5f95a23a088db24479c67461fcf497e6`
- workflow: `paper-operating-envelope`
- workflow run: `#26`
- run ID: `37106664614`
- artifact ID: `11267104157`
- artifact digest: `sha256:f3e6fe8ffac63168d878447bfd61f297f442a55c20b742e4def0374027350099`

### Headline robustness results at N=100

**Pairing sensitivity, R=1,G=0, adaptive link selection**

| Pairing | Mean desired distance | Mean SINR | First-TX success | Expected goodput |
|---|---:|---:|---:|---:|
| Sequential disjoint | 517.20 m | -23.03 dB | 0.0128 | 0.359 Mbps |
| Nearest-neighbour disjoint | 84.05 m | -1.75 dB | 0.4766 | 15.116 Mbps |

The original severe density collapse is therefore **not topology invariant**.

**Allocator sensitivity, R=8,G=0**

- sequential pairing: conflict graph `0.2049 / 1.042 Mbps` success/goodput vs random `0.1463 / 0.815 Mbps`;
- nearest-neighbour pairing: conflict graph `0.9465 / 10.836 Mbps` vs random `0.8824 / 8.357 Mbps`.

**Link-adaptation sensitivity, sequential pairing, R=8,G=6**

- adaptive: success `0.5292`, goodput `2.229 Mbps`;
- fixed MCS-4: success `0.3309`, goodput `0.722 Mbps`.

**Noise-bandwidth accounting**

Across the overlapping robustness grid, exact PRB occupied-bandwidth accounting changes mean SINR by at most `0.113 dB`, success by less than `7.4e-5`, and expected goodput by less than `3.1e-4 Mbps` relative to the frozen nominal-channel PRB-share convention.

## Publication interpretation

The paper must no longer claim that density alone universally drives UAV sidelink collapse. The supported statement is that the evaluated full-load long-link baseline becomes aggregate-interference limited as N grows, while topology-aware short-link pairing changes the regime dramatically. Resource coordination and spatial selectivity remain beneficial within the evaluated topologies.
