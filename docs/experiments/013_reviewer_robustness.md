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
