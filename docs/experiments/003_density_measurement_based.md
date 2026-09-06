# Experiment 003 — Swarm-density study with measurement-derived A2A propagation

## Objective

Quantify how increasing the number of UAVs changes interference and SINR in a controlled same-resource stress-test while using a measurement-derived 3.5 GHz A2A path-loss model.

## Scientific basis

Propagation and radio anchors come from Erdemir et al. (IEEE VTC 2023-Spring):

- 3.5 GHz carrier;
- 50 MHz sounding bandwidth;
- 30 dBm transmitted power;
- 100 m A2A altitude;
- fitted A2A large-scale path-loss parameters `eta=2.166`, `PL0=34.650 dB`.

The many-UAV scenario itself is not measured. Swarm size, placement, pairing, simultaneous reuse, receiver noise figure and SINR threshold are experimental/synthetic quantities documented in `config/density_measurement_based.yaml` and `references/parameter_sources.md`.

## Experimental sweep

- UAV counts: 5, 10, 20, 30, 50;
- 100 deterministic random seeds per UAV count;
- equal altitude: 100 m;
- synthetic uniform x/y positions inside 1000 m x 1000 m;
- half-duplex-compatible disjoint desired links `(0->1), (2->3), ...`;
- for odd N, the final UAV is idle in that snapshot;
- all active pairs reuse one resource in the baseline stress-test.

The disjoint-pair construction is intentional: it prevents a receiver from simultaneously transmitting on the same resource and removes artificial self-interference from the original ring prototype.

## Metrics

Raw link-level outputs include:

- 3D distance;
- path loss;
- received desired power;
- aggregate co-channel interference;
- SIR;
- SINR;
- threshold-based outage/link-success proxy;
- Shannon capacity upper bound.

The threshold proxy is **not NR packet delivery ratio** and the Shannon value is **not NR user throughput**.

Per-seed and aggregate summaries include mean, median, standard deviation, 5th/95th percentile and a 95% confidence interval for the mean SINR where applicable.

## Reproduction

```bash
python -m simulations.density_measurement_based
```

Outputs:

- `results/density_measurement_based/raw_links.csv`
- `results/density_measurement_based/per_seed.csv`
- `results/density_measurement_based/summary.csv`
- `figures/density/mean_sinr_vs_swarm_size.{png,pdf}`
- `figures/density/outage_proxy_vs_swarm_size.{png,pdf}`
- `figures/density/sinr_cdf.{png,pdf}`

## Interpretation

This experiment answers a system-level question: under a fixed synthetic traffic/reuse rule, how does swarm density affect interference and SINR when propagation is grounded in a measured A2A fit?

It does **not** claim that the generated UAV locations, interferers, SINR, outage or throughput are field measurements.

## Limitations / next step

- sensitivity-test receiver noise figure and SINR threshold;
- compare propagation choices using identical geometry/seeds;
- replace the all-on-one-resource stress-test with an NR Sidelink resource-selection abstraction;
- replace the threshold success proxy with an MCS/BLER mapping before reporting PDR-like metrics as final thesis results.
