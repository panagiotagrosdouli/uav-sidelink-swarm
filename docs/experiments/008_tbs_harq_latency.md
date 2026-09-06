# Experiment 008 — TBS/CBS-aware reliability and HARQ latency

## Goal

Replace bandwidth-times-spectral-efficiency approximations with a transport-block-aware layer and quantify the latency/reliability effect of retransmissions without claiming a bit-accurate sidelink implementation.

## Standards-grounded quantities

- **3GPP TS 38.214 V19.4.0**: MCS and transport-block-size determination used for PSSCH.
- **3GPP TS 38.212 V19.4.0**: LDPC base-graph selection and code-block segmentation.
- **3GPP TS 38.104** transmission-bandwidth table: 50 MHz at 30 kHz SCS corresponds to **133 PRBs** in FR1.
- NR numerology `mu=1`: **0.5 ms slot duration**.

## Link-level BLER input

The current repository test/study fixture uses the verified 5G-LENA EESM subset for Table-1, BG1, CBS=4096 and MCS 4/5/6. These values are classified `LINK_LEVEL_SIMULATION`, not UAV field measurements and not 3GPP-standard BLER curves.

The upstream importer can extract additional code-block-size/MCS curves from the pinned 5G-LENA numerical source when the complete upstream source file is supplied.

## Derived TB reliability

For a transport block split into `C` code blocks, the Python system-level abstraction maps the closest sourced CBS curve and calculates

`TB_BLER = 1 - (1 - CB_BLER)^C`.

This independence assumption is `DERIVED / SYSTEM_LEVEL_APPROXIMATION`.

## HARQ scope

5G-LENA v5.0 supports EESM HARQ Chase Combining (CC) and Incremental Redundancy (IR). This repository does **not** duplicate the complete 5G-LENA history-processing implementation.

The implemented Python HARQ study is explicitly **ideal Chase Combining**: repeated observations of the same coded packet are combined by summing linear SINR before re-evaluating the sourced BLER curve.

No arbitrary IR gain is invented.

## Configuration-sensitive quantities

The exact PSCCH/PSSCH DM-RS overhead and PSFCH/retransmission timing depend on sidelink resource-pool/scheduling configuration. Therefore:

- the current smoke-study data grid uses `DMRS_RE_PER_PRB=0` and `OTHER_OVERHEAD_RE_PER_PRB=0`, which makes the TBS result an **ideal PHY upper-bound profile**, not final sidelink throughput;
- `feedback_retx_gap_slots = 1, 2, 4, 8` is an `EXPERIMENTAL_SWEEP`, not a measured or universal NR value.

Before final thesis throughput/latency figures, replace the ideal overhead with one exact, cited sidelink PSCCH/PSSCH/DM-RS/PSFCH configuration.

## Reproduce

```bash
python -m simulations.harq_tbs_latency_study
```

Outputs:

- `results/harq_tbs_latency/per_link.csv`
- `results/harq_tbs_latency/summary.csv`

Key fields include selected MCS, TBS, LDPC base graph, number of code blocks, requested/used CBS curve, first-transmission TB BLER, success after capped ideal CC attempts, expected attempts, expected latency, and expected delivered goodput.
