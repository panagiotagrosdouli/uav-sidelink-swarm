# Submission readiness audit

This gate separates the broader thesis campaign from the paper-specific publication evidence.

## Broader thesis evidence

- Canonical thesis scientific commit: `fcae537ef0846b94c0c73ce306e15c406ab542f7`
- Final-thesis-campaign: run #5
- Registered experiments: `18/18 successful`
- Canonical figures: `17/17 present`
- Scientific audit checks: `304`
- Scientific audit failures: `0`

These results provide background context. They are not automatically the numerical source for the paper.

## Reviewer-hardened publication evidence

The paper-specific source is the `paper-operating-envelope` publication workflow, with exact metadata recorded in `docs/experiments/013_reviewer_hardened_publication_evidence.md`.

Primary N=100 controlled-regime evidence:

- R=1,G=0: mean SINR `-23.03 dB`, first-TX success `0.0128`, expected PHY goodput `0.359 Mbps`;
- R=8,G=6: mean SINR `0.53 dB`, first-TX success `0.5292`, expected PHY goodput `2.229 Mbps`.

Matched R=8,G=6 minus R=1,G=0 effects over 100 deterministic seeds:

- first-TX success: `+0.516362`; Student-t 95% CI `[0.505703, 0.527021]`; bootstrap 95% CI `[0.505738, 0.526751]`; Cohen `dz=9.61`; Wilcoxon `p=3.90e-18`;
- expected PHY goodput: `+1.870088 Mbps`; Student-t 95% CI `[1.726815, 2.013360]`; bootstrap 95% CI `[1.716869, 2.003005]`; `dz=2.59`; Wilcoxon `p=4.34e-17`.

## Required boundary-condition evidence

### Allocation

At N=100,G=0, matched random allocation versus the primary conflict-graph allocator must remain visible in the manuscript. For R=8:

- random: success `0.1463`, goodput `0.815 Mbps`;
- conflict graph: success `0.2049`, goodput `1.042 Mbps`;
- matched success difference: `+0.0586`, bootstrap 95% CI `[0.0510, 0.0658]`;
- matched goodput difference: `+0.226 Mbps`, bootstrap 95% CI `[0.186, 0.268]`.

Therefore the R=8,G=0 crossing of the 1 Mbps policy target is not attributed to resource partitioning alone.

### Pairing

At N=100,R=1,G=0:

- primary geometry-independent pairing: mean desired distance `517.2 m`, success `0.0128`, goodput `0.359 Mbps`;
- nearest-neighbour pairing: mean desired distance `84.0 m`, success `0.4766`, goodput `15.12 Mbps`;
- matched success difference: `+0.4637`, bootstrap 95% CI `[0.4539, 0.4736]`.

Therefore the primary envelope is a controlled non-local-peer regime and not a universal local-swarm capacity statement.

## Claim-preserving requirements

1. A2A propagation is a fitted measurement-derived large-scale model; simulated RF values are model-derived.
2. 5G-LENA BLER is `LINK_LEVEL_SIMULATION` evidence, not 3GPP-standard BLER data or UAV measurements.
3. Conflict-graph allocation is `THIS_WORK`, not normative Mode 1/2.
4. Directional `G` is an experimental desired/interferer relative advantage, not measured beamforming gain or full MIMO.
5. Reliability means modeled first-transmission success, not measured PDR.
6. Goodput means expected PHY goodput under the model, not end-to-end application throughput.
7. The envelope is the largest **evaluated** N under explicit policy thresholds and explicit topology/allocation assumptions.
8. Pairing locality must be stated whenever interpreting density scaling.
9. TBS-aware MCS selection is a `THIS_WORK` informed link-adaptation abstraction, not normative AMC.
10. Full fast fading, measured swarm RF, measured PDR/BLER/latency, and beam tracking are not claimed.

## Editorial and release gate

Before upload:

- all manuscript numbers must match the final hardened artifact;
- use a compact system-parameter table in the paper;
- effect magnitudes and confidence intervals must receive more emphasis than tiny p-values;
- references must be verified against publisher/DOI records;
- venue-specific formatting must be applied only after scientific content is frozen;
- final authorship/order, affiliations, corresponding-author details, funding/acknowledgements, and repository license require human confirmation;
- supervisor/co-author approval is required;
- a final rendered-PDF visual and reference audit is required.

See also `paper/REVIEWER_READINESS.md` and GitHub issue #30.

## Status

The implementation is reviewer-hardened, but **submission-ready status is granted only after the final publication workflow associated with the synchronized manuscript succeeds and its artifact is recorded in the evidence freeze**.
