# NR link-performance provenance

This project separates **3GPP STANDARD** MCS parameters from **LINK_LEVEL_SIMULATION** SINR-to-BLER curves. They are not the same type of evidence.

## 1. 3GPP MCS parameters

Primary source: **3GPP TS 38.214 V19.4.0 (Release 19)**.

For sidelink PSSCH, Clause 8.1.3.1 determines the modulation order `Qm` and target code rate `R` from the selected MCS table. The default Table-1 values reproduced in `src/sidelink/nr_mcs.py` come from **Table 5.1.3.1-1**.

Classification: `STANDARD`.

Implemented non-reserved indices: `I_MCS = 0..28`.

For each index the repository stores:

- modulation order `Qm`;
- target code rate `R x 1024`;
- spectral efficiency.

Reserved indices 29-31 are intentionally rejected by the API.

Official publication used for the implementation:

- ETSI TS 138 214 V19.4.0 (2026-07), 3GPP TS 38.214 version 19.4.0 Release 19.

## 2. SINR-to-BLER data

3GPP TS 38.214 does **not** provide a universal measured BLER-vs-SINR curve for every radio/channel/receiver realization. Therefore the old fixed `SINR >= 5 dB` link-success proxy must not be replaced by an invented curve.

The new reference source is the **5G-LENA EESM error model**, maintained by CTTC for ns-3 NR system-level simulation. 5G-LENA documents that its Table-1 error model contains:

- MCS Table-1 effective code rates;
- modulation orders;
- EESM beta values;
- SINR-to-BLER curves by MCS, LDPC base graph and code-block size.

Classification: `LINK_LEVEL_SIMULATION`, not `MEASURED` and not `3GPP_STANDARD`.

Primary software/source references:

- 5G-LENA nr module, CTTC, current documentation/source for `nr-eesm-t1.cc`;
- N. Patriciello, S. Lagen, B. Bojovic, L. Giupponi, *An E2E simulator for 5G NR networks*, SIMPAT 96 (2019), 101933, DOI 10.1016/j.simpat.2019.101933;
- 5G-LENA v5.0 software archive, DOI 10.5281/zenodo.21165297.

## 3. Verified repository fixture

`data/reference/5glena_table1_bg1_cbs4096_subset.csv` contains a deliberately small verified fixture for:

- Table 1;
- LDPC Base Graph 1;
- code-block size 4096 bits;
- MCS 4, 5 and 6.

The fixture exists to regression-test interpolation and the new link-performance pipeline. It is **not** claimed to cover the entire MCS space.

The full upstream table should be extracted locally from `nr-eesm-t1.cc` using:

```bash
python tools/extract_5glena_bler.py /path/to/nr-eesm-t1.cc data/processed/5glena_table1_bg1.csv
```

The project intentionally does not vendor the complete GPL-2.0-only upstream C++ file.

## 4. Derived metrics

Given a sourced BLER curve:

`first_tx_success_probability = 1 - BLER(SINR)`

This is `DERIVED_FROM_LINK_LEVEL_SIMULATION`.

The current expected PHY goodput is:

`bandwidth * standards_spectral_efficiency(MCS) * (1 - BLER)`

Classification: `DERIVED_SYSTEM_LEVEL_METRIC`.

It does not yet account for all PSSCH/PSCCH/DMRS resource overhead, guard bands, MAC/RLC/IP headers, scheduler loss or HARQ timing. It must not be called measured throughput.

## 5. HARQ warning

`independent_attempt_success_probability()` is provided only as an explicit sensitivity approximation. It is **not** Chase Combining or Incremental Redundancy HARQ and must not be reported as final NR HARQ performance.

For final HARQ results, use a sourced combining-aware model such as the corresponding 5G-LENA CC/IR EESM implementations or a validated bit-accurate link simulator.

## 6. What is now real/sourced vs still experimental

| Quantity | Classification |
|---|---|
| MCS index -> Qm/code-rate/SE | STANDARD (3GPP TS 38.214 V19.4.0) |
| 5G-LENA SINR->BLER points | LINK_LEVEL_SIMULATION |
| first-transmission success probability | DERIVED_FROM_LINK_LEVEL_SIMULATION |
| expected PHY goodput | DERIVED_SYSTEM_LEVEL_METRIC |
| swarm size / geometry / traffic | EXPERIMENTAL or SYNTHETIC |
| receiver noise figure 7 dB | EXPERIMENTAL_ASSUMPTION until sourced |
| full NR HARQ latency | NOT YET VALIDATED |
| measured UAV-swarm PDR | NOT AVAILABLE |
