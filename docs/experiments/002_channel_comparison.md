# Experiment 002 — A2A path-loss model comparison

## Objective

Compare three large-scale propagation models at a common carrier frequency and equal UAV altitude:

1. free-space path loss (FSPL), used only as a reference;
2. the measurement-derived A2A fit reported by Erdemir et al.;
3. the 3GPP Release-19 aerial-UE-to-aerial-UE Case-9 UMi-AV LOS model.

## Sources

- U. Erdemir et al., IEEE VTC 2023-Spring, DOI 10.1109/VTC2023-Spring57618.2023.10199853.
- 3GPP TR 38.901 V19.4.0, Clause 7.9.3, Case 9 and Table 7.9.3-5.
- 3GPP TR 36.777, Annex B, Tables B-1 to B-3.

## Common scenario

- carrier frequency: 3.5 GHz;
- equal UAV altitude: 100 m;
- link distance sweep: 10 m to 2000 m;
- no random shadow fading in this first deterministic comparison.

The 3GPP implementation is deliberately limited to the equal-height UMi-AV large-scale LOS branch. It is not a full fast-fading channel model.

## Equations

Measurement-derived fit:

`PL(d) = 34.650 + 10 * 2.166 * log10(d / 1 m)`

The UMi-AV LOS branch follows TR 36.777 Table B-2 and is selected for A2A use by TR 38.901 Case 9.

## Reproduction

```bash
python -m simulations.channel_comparison
```

Outputs:

- `results/channel_comparison/pathloss_comparison.csv`
- `figures/pathloss/pathloss_comparison.png`
- `figures/pathloss/pathloss_comparison.pdf`

## Interpretation rule

The Erdemir curve is a **measurement-derived fitted model**, not the raw measured samples. The 3GPP curve is a **standards-based model**. The FSPL curve is an analytical reference.

## Limitations

- no small-scale fading;
- no measured raw IQ/CIR samples;
- equal-altitude restriction for the initial A2A Case-9 implementation;
- no NR PHY/MAC effects.
