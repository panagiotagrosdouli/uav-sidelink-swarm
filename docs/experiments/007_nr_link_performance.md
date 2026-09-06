# Experiment 007 — Sourced NR MCS / BLER link-performance layer

## Objective

Replace the preliminary fixed-SINR link-success proxy with a provenance-aware link-performance layer.

## Evidence types

This experiment deliberately combines two different source classes:

1. **3GPP STANDARD**: MCS index, modulation order, target code rate and spectral efficiency from TS 38.214 V19.4.0.
2. **LINK_LEVEL_SIMULATION**: SINR-to-BLER curves from the CTTC 5G-LENA EESM model.

Neither category is labelled as a UAV field measurement.

## Implemented standard table

`src/sidelink/nr_mcs.py` implements non-reserved MCS Table-1 indices 0 through 28 from TS 38.214 Table 5.1.3.1-1. Reserved indices 29-31 are rejected.

## BLER source and scope

`data/reference/5glena_table1_bg1_cbs4096_subset.csv` is a small regression fixture extracted from the upstream 5G-LENA `nr-eesm-t1.cc` Table-1 data for:

- LDPC Base Graph 1;
- code-block size 4096;
- MCS 4, 5 and 6.

The full upstream dataset is intentionally not vendored. Use `tools/extract_5glena_bler.py` with a local copy of the official source file for a full extraction.

## Derived quantities

For a link with SINR `gamma` and selected MCS:

- `BLER(gamma)` is interpolated from sourced points;
- first-transmission success probability = `1 - BLER(gamma)`;
- expected PHY goodput = `B * SE(MCS) * (1 - BLER)`.

The expected goodput is not measured throughput. It omits several sidelink overhead and timing effects.

## Link adaptation

`src/sidelink/link_adaptation.py` selects the available MCS with maximum expected PHY goodput. This selection rule is `THIS_WORK / SYSTEM_LEVEL_ALGORITHM`; it is not a normative 3GPP AMC rule.

## Swarm experiment

Run:

```bash
python -m simulations.nr_link_performance_study
```

The script reuses the measurement-derived 3.5 GHz A2A propagation baseline and the existing synthetic density geometry. It runs 100 seeds for 5/10/20/30/50 UAVs and exports:

- SINR;
- selected MCS;
- BLER;
- first-transmission success probability;
- expected PHY goodput.

Outputs:

- `results/nr_link_performance/per_link.csv`
- `results/nr_link_performance/summary.csv`

## Critical limitations

- Only MCS 4/5/6 at BG1/CBS4096 are included in the repository fixture.
- This is not yet full PSSCH transport-block segmentation across arbitrary TBS.
- HARQ CC/IR combining is not yet applied.
- Full PSCCH/PSSCH/DMRS overhead and scheduler timing are not yet included.
- The existing 7 dB receiver noise figure remains an experimental assumption.

Therefore use the current experiment to replace the crude threshold proxy for a **validated subset**, not to claim complete bit-accurate NR Sidelink performance.
