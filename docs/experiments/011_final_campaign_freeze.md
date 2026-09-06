# Experiment 011 — Canonical final campaign freeze

## Canonical execution

- Campaign: `final_uav_nr_sidelink_experimental_campaign`
- Canonical Git commit: `c293502a7410edf0c5c4cc982da9b449093b832b`
- GitHub Actions workflow: `final-thesis-campaign`
- Workflow run: `34029037140`
- Generated UTC: `2026-09-06T11:07:59.730082+00:00`
- Python: `3.12.14`
- Campaign configuration: `config/final_campaign.yaml`
- Monte-Carlo seeds: `100`
- Swarm sizes: `5, 10, 20, 30, 50, 75, 100`

## Validation status

All registered experiments completed with return code 0. The finalizer completed successfully and the generated scientific audit reported **zero failures**.

Registered successful experiments:

1. measurement-derived A2A propagation baseline
2. channel-model comparison
3. density study
4. scaling / geometry / activity study
5. scaling-law descriptive analysis
6. resource-allocation study
7. routing study
8. directionality sensitivity
9. physical ULA array-factor study
10. robustness sensitivity
11. NR MCS/BLER link performance
12. TBS/CBS/HARQ latency study
13. sidelink resource-overhead sensitivity
14. traffic-load study
15. failure analysis
16. spatial diagnostics
17. cross-layer ablation
18. paired effect-size/statistical analysis

## Canonical artifact

- Artifact ID: `9988077594`
- Name: `final-thesis-campaign-c293502a7410edf0c5c4cc982da9b449093b832b`
- Size: `2,368,177 bytes`
- SHA-256 digest: `51d6f646682f3ce185a6e305da670feeebdd235a96567d8f004ca74d8a7555da`
- Created: `2026-09-06T11:08:01Z`
- Expiration: `2026-12-05T11:01:30Z`

The artifact contains canonical summary CSVs, reproducibility metadata, scientific audit output, and thesis-ready PDF/PNG figures.

## Evidence-backed observations

The generated final-campaign findings report:

- fixed-area mean SINR changes from `7.52 dB` at `N=5` to `-1.75 dB` at `N=100`, with final-point 95% CI `[-1.89, -1.61] dB`;
- the fixed-density family shows the same reported endpoint values under the current synthetic scaling experiment;
- at `N=100`, the highest mean modeled goodput among evaluated ablation mechanisms is `adaptive_directional6_shared` at `0.316 Mbps`;
- at `N=50`, the highest mean derived PHY goodput in the resource-allocation grid is produced by `greedy` allocation with `8` abstract resources at `1.471 Mbps`.

These are **system-level simulation/derived results**, not measured UAV throughput or measured packet-delivery results.

## External-data limitation

The canonical AMOVFLY real-mobility figure is not included because raw AMOVFLY telemetry is external and is not vendored into this repository. The common-frame WGS84/ECEF/ENU processing path is implemented, but a real-mobility canonical run requires user-supplied AMOVFLY files.

## Explicit non-claims

This campaign does not claim:

- bit-accurate NR Sidelink PHY;
- normative Mode-2 scheduler implementation;
- exact HARQ incremental-redundancy history;
- full fast fading;
- full MIMO beam management;
- measured swarm RF PDR;
- measured end-to-end latency.

This commit records the canonical experimental evidence state. Any later scientific change that affects results should produce a new campaign commit/run rather than silently replacing this freeze.
