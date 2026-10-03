# Paper track — NR Sidelink UAV Swarm Operating Envelope

## Publication status

**Status: submission draft / research manuscript.**

The material in this directory is prepared for scientific submission and reproducibility review. It is **not currently represented in this repository as an accepted or published IEEE conference/journal paper**, and no publication DOI, proceedings pages, or acceptance record is claimed here.

`VTC2027-Spring` files are venue-planning and manuscript-compression material only. If the work is later accepted or published, this section and `CITATION.cff` should be updated with the formal bibliographic record.

## Working title

**Interference Scaling and Cross-Layer Mitigation in 5G NR Sidelink UAV Swarms**

## Central research question

> How does UAV swarm density change the interference regime of NR sidelink, and how far can resource separation and spatial directionality extend the feasible reliability/goodput operating region?

This paper is deliberately narrower than the full project campaign. It does **not** attempt to report every implemented experiment.

## Core contributions

1. **Measurement-grounded, NR-aware system framework.** Large-scale A2A propagation is anchored in the Erdemir et al. 3.5 GHz measurement-derived fit; NR MCS/TBS/LDPC mechanics are standards-based; numerical SINR-to-BLER evidence is sourced from verified 5G-LENA link-level simulation data where available.
2. **Density-dependent interference-regime characterization.** Quantify SINR, BLER, first-transmission success, expected PHY goodput, and failure composition as swarm size increases.
3. **Conditional operating envelope with reviewer robustness.** Quantify the interaction among swarm size, exact resource separation, conflict-aware versus random assignment, directional desired/interference advantage, and peer-pairing locality, and derive an explicitly conditional evaluated operating envelope rather than a universal capacity limit.

## Paper-specific experiment

Evaluate the Cartesian grid:

- `N = [5, 10, 20, 30, 50, 75, 100]`
- abstract orthogonal resources `R = [1, 2, 4, 8]`
- directional relative advantage `G = [0, 3, 6, 9] dB`
- 100 deterministic seeds in full mode
- canonical measurement-derived A2A propagation and NR-aware link evaluation
- primary geometry-independent disjoint pairing, with nearest-neighbour disjoint pairing as a matched-seed sensitivity
- primary weighted conflict-graph assignment, with matched-seed random allocation as a baseline
- occupied noise bandwidth computed exactly from allocated PRBs: `n_PRB × 12 × 30 kHz`

For each `(N,R,G)`, report mean and 95% CI for:

- SINR
- TB BLER / first-TX success
- expected PHY goodput
- Jain fairness where applicable
- aggregate-vs-dominant interference composition

Derive an **operating envelope** rather than a universal capacity limit. For explicitly declared targets, compute the largest evaluated `N` satisfying the target for each `(R,G)` combination **under the primary pairing and allocator**. Targets are experimental engineering policies, not 3GPP requirements. Random-allocation and nearest-neighbour-pairing sensitivities are reported separately so the primary envelope is not over-generalized.

## Primary figures

1. Mean SINR / success vs swarm size for selected `(R,G)` configurations.
2. Heatmap: first-TX success over `(N,R)` for each directional advantage.
3. Heatmap: expected goodput over `(N,R)` for each directional advantage.
4. Operating-envelope plot: largest evaluated swarm size meeting explicit reliability/goodput targets vs resources and directionality.
5. Failure-regime composition vs density for baseline and one mitigated configuration.

## Evidence separation

The repository contains two related but distinct evidence contexts that must not be numerically mixed.

### Background full-campaign evidence

The broader final campaign at scientific commit `fcae537ef0846b94c0c73ce306e15c406ab542f7` establishes system-level background findings across the wider project, including density collapse, resource-allocation behavior, directionality sensitivity, failure composition, and HARQ behavior. Those outputs provide context and cross-checks, but they are **not automatically the numerical source for tables or claims in this paper**.

### Paper-specific frozen evidence

Numerical claims in `MANUSCRIPT_SUBMISSION.md` are tied to the paper-specific `paper-operating-envelope` frozen experiment and its exact `(N,R,G)` configuration. In particular, the manuscript's baseline and mitigated values must be taken from that paper-specific evidence rather than substituted with superficially similar values from other campaign experiments.

The reviewer-hardened paper experiment reports, among other results, the primary `N=100, R=1, G=0` controlled-regime baseline as mean SINR `-23.03 dB`, first-TX success `0.0128`, and expected PHY goodput `0.359 Mbps`. Under nearest-neighbour disjoint pairing with the same N/R/G, first-TX success is `0.4766` and expected goodput is `15.12 Mbps`. This large difference is a required boundary condition: the primary envelope isolates a non-local geometry-independent peer regime and must not be presented as universal local-swarm performance.

Different numerical values from the broader campaign are not necessarily contradictions: they may correspond to different experiment definitions, configurations, or link-evaluation paths. Any comparison across evidence contexts must therefore state the experiment provenance explicitly.

All of these quantities are simulation/model-derived outputs, not measured swarm RF results.

## Scientific boundaries

The paper must not claim:

- measured swarm RF/PDR/latency;
- a bit-accurate NR sidelink PHY;
- normative Mode-1/Mode-2 scheduling;
- full MIMO or beam management;
- exact HARQ IR processing;
- a universal maximum UAV swarm size.

The directional parameter remains an `EXPERIMENTAL_SWEEP` unless replaced by a separately validated physical beamforming model. Resource algorithms and pairing policies remain `THIS_WORK` abstractions. The TBS-aware MCS selection is also a model-based `THIS_WORK` link-adaptation rule, not normative NR AMC.

## Evidence rule

Every paper table/figure must be reproducible from a committed experiment, record seed/configuration provenance, and distinguish `STANDARD`, `LITERATURE`, `LINK_LEVEL_SIMULATION`, `DERIVED_SYSTEM_LEVEL_METRIC`, `EXPERIMENTAL_CONFIGURATION`, `EXPERIMENTAL_SWEEP`, and `THIS_WORK` quantities.

For submission claims, `MANUSCRIPT_SUBMISSION.md` and its explicitly recorded paper-specific evidence freeze take precedence over background numbers quoted from other project campaigns.