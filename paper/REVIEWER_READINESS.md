# Reviewer-readiness gate

This checklist defines the minimum scientific and editorial conditions for treating
the UAV sidelink manuscript as submission-ready. Passing repository tests alone
is not sufficient.

## 1. Scientific model disclosure

The manuscript must state, in the paper itself:

- carrier frequency: 3.5 GHz;
- nominal channel profile: 50 MHz, 30 kHz SCS, 133 PRBs;
- occupied noise bandwidth: allocated PRBs x 12 subcarriers x 30 kHz;
- transmit power: 30 dBm;
- receiver noise figure: 7 dB;
- deployment area: 1000 m x 1000 m;
- equal UAV altitude: 100 m;
- activity probability: 1.0 for the primary operating-envelope experiment;
- primary pairing: deterministic sequential disjoint pairs;
- primary allocator for R>1: THIS_WORK weighted conflict graph;
- primary channel: measurement-derived 3.5 GHz A2A large-scale path-loss fit;
- link adaptation: THIS_WORK TBS-aware selection maximizing modeled first-TX
  expected delivered bits per slot over sourced MCS/BG/CBS BLER curves.

These are study assumptions, not universal NR sidelink parameters.

## 2. Reviewer sensitivity requirements

The publication evidence must contain matched-seed robustness checks for:

### Resource allocator

Random resource assignment versus THIS_WORK weighted conflict-graph allocation,
holding N, R, G, geometry seed, resource bandwidth, TBS/LDPC mapping and BLER
evidence fixed.

Required outputs:

- allocator_per_seed.csv
- allocator_summary.csv
- allocator_paired_effects.csv

### Pairing

Sequential disjoint pairing versus nearest-neighbour disjoint pairing, holding
the geometry seed and remaining scenario definition fixed.

Required outputs:

- pairing_per_seed.csv
- pairing_summary.csv
- pairing_paired_effects.csv

The paper must not attribute all R>1 improvement to resource partitioning unless
the allocator contribution is separately acknowledged.

## 3. Statistical requirements

For headline matched-seed effects report:

- sample size;
- mean paired difference;
- Student-t 95% confidence interval;
- deterministic percentile-bootstrap 95% confidence interval;
- effect size (Cohen dz);
- a non-parametric paired sensitivity check (Wilcoxon signed-rank).

P-values are secondary. Magnitudes and confidence intervals are the primary
scientific evidence.

## 4. Claim boundaries

Allowed:

- evaluated operating envelope;
- simulation/model-derived first-transmission success;
- expected PHY goodput under the evaluated model;
- measurement-derived large-scale propagation model;
- sourced 5G-LENA link-level BLER evidence;
- controlled spatial-selectivity sensitivity.

Not allowed without new evidence:

- measured multi-UAV RF reliability/PDR/latency;
- universal maximum swarm size;
- standards-complete NR sidelink PHY/MAC;
- normative Mode-1/Mode-2 resource selection;
- measured beamforming gain;
- full MIMO/beam tracking;
- universal capacity claims.

## 5. Related-work positioning

The novelty claim must be limited to the combined, reproducible characterization
of density, exact PRB partitioning, sourced NR-oriented BLER/TBS mechanics,
resource-allocation sensitivity and spatial-selectivity sensitivity. The paper
must not claim novelty for the generic use of sidelink in UAV swarms.

Before submission, publisher/DOI metadata must be checked for every reference.

## 6. Reproducibility gate

A submission freeze must record:

- exact git commit;
- workflow run ID;
- artifact ID and digest;
- 100 deterministic seeds for the main publication grid;
- exact scenario dimensions;
- absence of unsupported BLER-curve lookups;
- matched-seed effect tables;
- reviewer-sensitivity tables;
- final manuscript version associated with the freeze.

Any scientific change after the freeze requires a new evidence run.

## 7. Editorial gate

Before upload:

- convert the manuscript to the official target-venue IEEE template;
- include a compact system-parameter table;
- keep the main paper focused on density, resource partitioning, allocation
  sensitivity and spatial selectivity;
- keep HARQ, routing, traffic and mobility as background/supplementary evidence
  unless the page budget explicitly allows them;
- verify author names, affiliations and acknowledgements with the human authors;
- verify the target venue's current submission and AI-assistance rules;
- obtain supervisor/co-author approval;
- perform a final PDF visual and reference audit.

## Status

The gate is passed only after the new reviewer-hardened publication workflow
completes successfully and the manuscript numbers are regenerated from that
exact artifact.
