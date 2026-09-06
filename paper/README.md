# Paper track — NR Sidelink UAV Swarm Operating Envelope

## Working title

**Interference Scaling and Cross-Layer Mitigation in 5G NR Sidelink UAV Swarms**

## Central research question

> How does UAV swarm density change the interference regime of NR sidelink, and how far can resource separation and spatial directionality extend the feasible reliability/goodput operating region?

This paper is deliberately narrower than the thesis. It does **not** attempt to report every implemented experiment.

## Core contributions

1. **Measurement-grounded, NR-aware system framework.** Large-scale A2A propagation is anchored in the Erdemir et al. 3.5 GHz measurement-derived fit; NR MCS/TBS/LDPC mechanics are standards-based; numerical SINR-to-BLER evidence is sourced from verified 5G-LENA link-level simulation data where available.
2. **Density-dependent interference-regime characterization.** Quantify SINR, BLER, first-transmission success, expected PHY goodput, and failure composition as swarm size increases.
3. **Cross-layer operating envelope.** Quantify the interaction among swarm size, orthogonal resource separation, and directional desired/interference advantage, and derive the maximum supported swarm size under explicit reliability/goodput targets.

## Paper-specific experiment to add

Evaluate the Cartesian grid:

- `N = [5, 10, 20, 30, 50, 75, 100]`
- abstract orthogonal resources `R = [1, 2, 4, 8]`
- directional relative advantage `G = [0, 3, 6, 9] dB`
- 100 deterministic seeds in full mode
- canonical measurement-derived A2A propagation and NR-aware link evaluation

For each `(N,R,G)`, report mean and 95% CI for:

- SINR
- TB BLER / first-TX success
- expected PHY goodput
- Jain fairness where applicable
- aggregate-vs-dominant interference composition

Derive an **operating envelope** rather than inventing a universal capacity limit. For explicitly declared targets, compute the largest evaluated `N` satisfying the target for each `(R,G)` combination. Targets are experimental engineering policies, not 3GPP requirements.

## Primary figures

1. Mean SINR / success vs swarm size for selected `(R,G)` configurations.
2. Heatmap: first-TX success over `(N,R)` for each directional advantage.
3. Heatmap: expected goodput over `(N,R)` for each directional advantage.
4. Operating-envelope plot: maximum evaluated swarm size meeting explicit reliability/goodput targets vs resources and directionality.
5. Failure-regime composition vs density for baseline and one mitigated configuration.

## Existing canonical evidence to reuse

Canonical thesis run #5 already establishes the baseline evidence at commit `fcae537ef0846b94c0c73ce306e15c406ab542f7`:

- shared-resource density collapse: mean SINR about `-0.49 -> -23.03 dB` from `N=5 -> 100`;
- first-TX success about `0.349 -> 0.006`;
- expected PHY goodput about `14.106 -> 0.248 Mbps`;
- at `N=50`, eight-resource greedy allocation reaches about `1.471 Mbps` mean expected PHY goodput in the existing resource study;
- directional sensitivity shows large recovery when desired gain and interference suppression act together;
- failure composition moves toward aggregate-interference dominance at high density;
- HARQ alone remains ineffective when first-transmission BLER is already near one.

These are simulation/model-derived outputs, not measured swarm RF results.

## Scientific boundaries

The paper must not claim:

- measured swarm RF/PDR/latency;
- a bit-accurate NR sidelink PHY;
- normative Mode-1/Mode-2 scheduling;
- full MIMO or beam management;
- exact HARQ IR processing;
- a universal maximum UAV swarm size.

The directional parameter remains an `EXPERIMENTAL_SWEEP` unless replaced by a separately validated physical beamforming model. Resource algorithms remain `THIS_WORK` abstractions.

## Evidence rule

Every paper table/figure must be reproducible from a committed experiment, record seed/configuration provenance, and distinguish `STANDARD`, `LITERATURE`, `LINK_LEVEL_SIMULATION`, `DERIVED_SYSTEM_LEVEL_METRIC`, `EXPERIMENTAL_CONFIGURATION`, `EXPERIMENTAL_SWEEP`, and `THIS_WORK` quantities.
