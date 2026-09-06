# 012 — Canonical full experimental campaign

## Objective

Implement the complete pre-thesis experimental evidence program requested by the
master specification. This is a research/engineering log, not diploma-thesis
prose.

## Canonical configuration

`config/final_campaign.yaml`

Full mode uses 100 deterministic seeds. CI smoke mode uses only the configured
small seed count and the verified small 5G-LENA BLER fixture.

## Link-performance provenance

- NR MCS/TBS/LDPC mechanics: `STANDARD`, exact Release-19 specification versions
  recorded by the project.
- Numerical SINR→BLER curves: `LINK_LEVEL_SIMULATION` from pinned 5G-LENA v5.0,
  fetched and processed at run time. The upstream GPL C++ source is not vendored.
- TBS-aware MCS selection: `THIS_WORK_LINK_ADAPTATION`.
- TB BLER from CB BLER: `DERIVED_SYSTEM_LEVEL_APPROXIMATION`, with independent
  code-block decoding assumption.
- HARQ: ideal Chase-Combining abstraction only; no fabricated IR gain.

## Experiment families

1. propagation-model comparison;
2. fixed-area and fixed-spatial-density scaling;
3. SINR CDFs;
4. synthetic formation/geometry sensitivity;
5. resource-count × activity × allocator interaction;
6. fixed-MCS vs adaptive-MCS comparison;
7. HARQ attempt/gap sensitivity;
8. desired-gain vs interference-suppression directionality;
9. channel-model uncertainty;
10. NF, transmit-power, altitude and sourced UMi-AV shadow-fading robustness;
11. offered-traffic/activity abstraction;
12. isolated-link direct/multi-hop routing abstraction;
13. synthetic random-waypoint mobility;
14. physical ULA array-factor extension;
15. incremental ablation;
16. failure-scenario extraction;
17. exploratory scaling-model fits.

## Real mobility

`simulations.real_mobility_amovfly_public` uses the pinned public AMOVFLY commit
`67069ed00ddbebd62b71aa9bb1272415e9b15ff8` and the simultaneous pair recorded
by `Multi-Uav_infosheet.csv`:

- `UavY_P0A10S6_1`, takeoff 2024/11/21 13:50;
- `UavR_P0A40VarS8_1`, takeoff 2024/11/21 13:46.

The raw CSV files are downloaded transiently and are not redistributed.
AMOVFLY documents `gps_x/gps_y` as local-to-takeoff coordinates, `gps_z` as
altitude above ground, and `real_lat/real_long` as actual global trajectory.
Therefore the multi-UAV analysis derives one shared horizontal WGS-84 ENU frame
from `real_lat/real_long` and retains measured AGL `gps_z` vertically.

Original telemetry: `MEASURED_DATASET`.
Synchronized/common-frame mobility: `DERIVED_FROM_MEASURED_DATASET`.
RF metrics after applying the Erdemir A2A model: `SIMULATION_USING_MEASURED_MOBILITY`.

## CI versus full run

Pull requests execute:

```bash
python -m simulations.final_experimental_campaign --smoke
```

This validates the complete pipeline without pretending that the smoke result is
the final statistical campaign.

After a scientific change reaches `main`, `.github/workflows/full-campaign.yml`
runs the pinned full-BLER ingestion, the 100-seed campaign and the public AMOVFLY
experiment, then uploads a frozen result/figure/config artifact tagged by Git SHA.

## Persistent non-claims

The campaign is not:

- a bit-accurate NR Sidelink PHY;
- a normative Mode-2 implementation;
- measured swarm RF interference/PDR/latency;
- complete HARQ IR/CC history processing;
- complete fast fading;
- complete MIMO or NR beam management.

These are reported as limitations rather than replaced with invented data.
