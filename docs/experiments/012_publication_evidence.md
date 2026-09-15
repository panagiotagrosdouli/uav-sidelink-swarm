# 012 — Canonical publication evidence freeze — HISTORICAL / SUPERSEDED

> **Current canonical status:** the repository README and `docs/FINAL_READINESS.md` now identify final-thesis-campaign run **#5** on scientific commit `fcae537ef0846b94c0c73ce306e15c406ab542f7` as the current canonical thesis evidence state. This file remains valuable as the earlier publication evidence freeze and is retained for provenance.

This file freezes the first publication-ready NR Sidelink UAV swarm operating-envelope campaign that includes the matched-seed statistical synthesis. It is evidence metadata only; it does not redefine the scientific model.

## Canonical scientific commit

- Scientific commit SHA: `9fb112307270d9d39408e704f285ea91d20a735b`
- Source branch at execution: `main`
- Workflow: `paper-operating-envelope`
- Workflow run number: `3`
- Workflow run ID: `34085307799`
- Workflow conclusion: `success`

All workflow gates completed successfully: unit tests, bundled-fixture smoke validation, official 5G-LENA v5.0 Table-1 preparation, full 100-seed operating-envelope campaign, matched-seed statistical synthesis, provenance generation, and artifact upload.

## Frozen artifact

- Artifact ID: `10005074790`
- Artifact name: `paper-operating-envelope-9fb112307270d9d39408e704f285ea91d20a735b`
- Artifact size: `1,702,538 bytes`
- Artifact digest: `sha256:4a996afe9dffa7984a5a0cfa6276a6f727228cd1ee2cbbd6e7f1634e8c149137`
- Artifact creation time: `2026-09-07T05:06:53Z`
- Artifact expiry recorded by GitHub: `2026-12-06T05:02:41Z`

## Campaign dimensions and audit

- Seeds per scenario: `100`
- Swarm sizes: `[5, 10, 20, 30, 50, 75, 100]`
- Orthogonal resource counts: `[1, 2, 4, 8]`
- Directional relative advantages: `[0, 3, 6, 9] dB`
- Per-seed realizations: `11,200`
- Scenario summaries: `112`
- Operating-envelope points: `16`
- Matched-seed comparisons: `84`
- Missing values in per-seed table: `0`
- Missing values in summary table: `0`
- Missing values in matched-seed table: `0`
- BLER curve mode in publication rows: `FULL_5GLENA_V5_LOCAL`
- Independent recomputation of the operating-envelope thresholds from `summary.csv`: exact match to `operating_envelope.csv`

## BLER evidence provenance

The numerical SINR-to-BLER curves are `LINK_LEVEL_SIMULATION` evidence from official CTTC 5G-LENA v5.0 Table-1 data, not measurements and not 3GPP-standard BLER curves.

- 5G-LENA version: `v5.0`
- Release short commit: `47a3adc2`
- DOI: `10.5281/zenodo.21165297`
- Source SHA-256: `979f3a52c1ec1031cbb570b1ff56fdcd8d5cee38f9a505baa19aae66b2d30c91`
- Processed BLER points: `9,648`
- Curves: `1,332`
- Base graphs: `BG1`, `BG2`
- MCS indices: `0–28`

## Resource and directionality semantics

- `STANDARD`: 50 MHz / 30 kHz SCS study profile uses 133 PRBs.
- `EXPERIMENTAL_CONFIGURATION`: the 133 PRBs are exactly partitioned across `R` orthogonal frequency resources. Per-resource occupied bandwidth, noise, TBS, LDPC segmentation, and sourced CBS lookup are recomputed.
- `THIS_WORK`: the conflict-graph allocator is a system-level resource-allocation abstraction, not normative NR Sidelink Mode 1/2 scheduling.
- `EXPERIMENTAL_SWEEP`: directional relative advantage `G` is modeled as `+G/2 dB` desired-link gain and `-G/2 dB` co-channel-interference gain. This is not full MIMO or beam management.

## Frozen operating envelope

The explicit engineering policy is:

- mean first-transmission success probability `>= 0.10`, and
- mean expected PHY goodput `>= 1.0 Mbps`.

These thresholds are `EXPERIMENTAL_CONFIGURATION` policy choices, not 3GPP requirements. The largest **evaluated** `N` satisfying both is:

| Resources R | G=0 dB | G=3 dB | G=6 dB | G=9 dB |
|---:|---:|---:|---:|---:|
| 1 | 10 | 10 | 20 | 50 |
| 2 | 50 | 75 | 100 | 100 |
| 4 | 50 | 75 | 100 | 100 |
| 8 | 100 | 100 | 100 | 100 |

This table is a `DERIVED_SYSTEM_LEVEL_METRIC_FROM_EXPERIMENTAL_POLICY_TARGETS`. It is not a universal maximum UAV swarm size.

## Frozen headline results at N=100

Baseline `R=1, G=0 dB`:

- mean SINR: `-23.03 dB`
- mean first-TX success: `0.013`
- mean expected PHY goodput: `0.359 Mbps`

Mitigated `R=8, G=6 dB`:

- mean SINR: `0.53 dB`
- mean first-TX success: `0.529`
- mean expected PHY goodput: `2.229 Mbps`

Matched deterministic-seed comparison, `R=8,G=6` versus `R=1,G=0` at `N=100`:

- First-TX success difference: `+0.516358`; 95% CI `[0.505829, 0.526887]`; Cohen `dz=9.6122`; paired-t `p=1.4474e-99`; `n=100` matched seeds.
- Expected PHY goodput difference: `+1.870079 Mbps`; 95% CI `[1.728555, 2.011603]`; Cohen `dz=2.5899`; paired-t `p=6.9415e-46`; `n=100` matched seeds.

These are `DERIVED_SYSTEM_LEVEL_METRIC_MATCHED_SEED_COMPARISON` results.

## Scientific interpretation boundary

The frozen evidence supports the statement that, in the evaluated measurement-grounded/system-level scenario, increasing swarm density drives shared-resource sidelink into a severe interference-limited regime, while frequency-resource separation and spatial desired/interferer advantage can substantially shift the feasible operating region. Exact PRB partitioning exposes a bandwidth-versus-interference trade-off, so more orthogonal resources do not automatically imply more goodput.

The evidence does **not** support claims of:

- measured multi-UAV RF interference, PDR, BLER, or end-to-end latency;
- a bit-accurate or standards-complete NR sidelink PHY/MAC implementation;
- normative Mode 1/Mode 2 resource selection;
- full MIMO, beam tracking, or beam management;
- a universal UAV swarm capacity limit;
- 3GPP-standard numerical BLER curves.

## Supersession

Publication run #1 at scientific SHA `8d28e57e97e2c16c03c4a45636a9e4083ce11c02` established the first full operating-envelope artifact. This run #3 supersedes it for manuscript evidence because it preserves the same publication experiment while adding the committed matched-seed statistical synthesis and publication manuscript path. The performance-only BLER lookup optimization merged before run #3 was regression-tested to preserve the historical nearest-CBS selection semantics exactly.
