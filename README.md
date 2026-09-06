# UAV Sidelink Swarm

Research-oriented Python simulation project for 5G/6G sidelink communication inside UAV swarms.

## Goal

Build a reproducible system-level simulator using parameters grounded in 3GPP specifications and published literature, and optionally ingest real UAV trajectory datasets when suitable.

## Data policy

This project distinguishes between:

1. **Measured/real datasets** — e.g. UAV trajectories or experimentally collected mobility data.
2. **Standards-based parameters** — channel, carrier, bandwidth, antenna and radio parameters taken from 3GPP documents or peer-reviewed publications.
3. **Synthetic scenarios** — generated only when no measured dataset is available, and always clearly labelled as synthetic.

No synthetic value should be presented as a real measurement.

## Planned metrics

- 3D UAV-to-UAV distance
- Path loss
- Received power
- SNR / SINR
- Packet delivery ratio
- Throughput
- Latency
- Outage probability
- Impact of swarm density and mobility
- Later extensions: interference-aware scheduling, MIMO and beamforming

## Initial scientific references

- A. Giannakoulas, N. Karkanis, S. Markou, G. Kyriacou, T. Kaifas, “Sidelink Communication for Unmanned Platforms' (UxU) Swarms in Challenging Scenarios,” CIEES 2025, DOI: 10.1109/CIEES66347.2025.11300255.
- 3GPP TR 38.767, “Uncrewed aerial vehicle (UAV) for NR,” Release 20 work in progress.

## Repository structure

```text
uav-sidelink-swarm/
├── data/
│   ├── raw/
│   └── processed/
├── src/
├── simulations/
├── results/
├── figures/
├── references/
└── README.md
```

## Reproducibility

Every experiment should record the source of each physical parameter, random seed, scenario geometry and software version so that thesis results can be reproduced.
