# Experiment 009 — NR sidelink resource-grid overhead

## Goal

Replace the previous zero-overhead PHY upper-bound profile with explicit PSSCH
resource accounting, while avoiding the scientifically incorrect claim that NR
sidelink has one universal PSCCH/DM-RS overhead percentage.

## Standards basis

- 3GPP TS 38.211 V19.4.0: NR physical channels and modulation; sidelink physical
  channels/reference-signal mapping.
- 3GPP TS 38.214 V19.4.0: PSSCH physical-layer procedures and TBS determination.
- Both are Release-19 specifications under change control; the repository records
  the exact version used.

## Fixed standard-derived radio profile

- Bandwidth: 50 MHz.
- SCS: 30 kHz.
- PRBs: 133.
- Normal-CP slot duration at mu=1: 0.5 ms.

## Explicit study configuration — NOT universal 3GPP values

The default thesis profile uses:

- 2 symbols reserved for PSCCH/control accounting,
- 1 guard symbol,
- 11 PSSCH symbols,
- 24 DM-RS RE/PRB across the PSSCH allocation.

These are `EXPERIMENTAL_CONFIGURATION` values. They provide a reproducible
non-zero-overhead baseline and are sensitivity-tested rather than described as
mandatory values for every NR sidelink resource pool.

## Sensitivity sweep

`python -m simulations.sidelink_overhead_sensitivity`

Sweeps:

- PSCCH/control symbols: 1, 2, 3;
- DM-RS overhead: 12, 24, 36 RE/PRB;
- MCS: 4, 5, 6, 10, 14, 20.

For each point it exports usable RE/PRB, TBS and TBS loss relative to the old
zero-overhead 14-symbol idealization.

## Interpretation rule

TBS quantization is `STANDARD`. The selected resource-pool/control/DM-RS profile
is `EXPERIMENTAL_CONFIGURATION`. Resulting TBS loss and goodput reduction are
`DERIVED`. No result from this experiment is a measured UAV packet trace.
