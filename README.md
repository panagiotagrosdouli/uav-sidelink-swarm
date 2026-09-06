# UAV Sidelink Swarm

Research-oriented Python system-level simulation project for 5G NR Sidelink communication inside UAV swarms.

## Thesis goal

Study how UAV swarm density and mobility affect UAV-to-UAV link quality, interference, reliability and network connectivity, then evaluate controlled improvements from resource allocation, routing and directional antenna gains.

The scientific pipeline is:

`SOURCE -> MODEL -> IMPLEMENTATION -> VALIDATION -> EXPERIMENT -> RESULT -> INTERPRETATION -> LIMITATIONS`

## Scientific data policy

Every important quantity is classified as one of:

- `MEASURED` / `MEASURED_DATASET`
- `STANDARD`
- `LITERATURE`
- `DERIVED`
- `EXPERIMENTAL_SWEEP`
- `EXPERIMENTAL_ASSUMPTION`
- `SYNTHETIC`

Synthetic simulation values are never presented as real measurements.

## Implemented research layers

### 1. Published measurement-derived A2A propagation

Primary peer-reviewed source:

U. Erdemir et al., **“Measurement-based Channel Characterization for A2A and A2G Wireless Drone Communication Systems,”** IEEE VTC 2023-Spring, DOI `10.1109/VTC2023-Spring57618.2023.10199853`.

The repository reproduces the reported A2A large-scale fit at 3.5 GHz using `eta=2.166` and `PL0=34.650 dB`. Values generated from this fit are labelled measurement-derived, not raw RF samples.

### 2. 3GPP Release-19 aerial-to-aerial large-scale channel

A deliberately limited and auditable equal-height UMi-AV A2A implementation is included from:

- 3GPP TR 38.901 V19.4.0, Clause 7.9.3, Case 9;
- 3GPP TR 36.777 Annex B aerial-UE LOS/NLOS and shadow-fading models.

This is not a full fast-fading or bit-accurate NR PHY implementation.

### 3. Common swarm interference simulator

The same geometry/power accounting can use:

- FSPL reference;
- measurement-derived A2A fit;
- 3GPP Case-9 UMi-AV LOS.

The simulator computes desired received power, aggregate co-channel interference, SIR, SINR, threshold-based outage/link-success proxies and a Shannon theoretical upper bound.

### 4. Density Monte Carlo study

The controlled baseline sweeps `N = 5, 10, 20, 30, 50` UAVs over 100 deterministic seeds. UAV coordinates are synthetic and half-duplex-compatible disjoint Tx/Rx pairs are used to avoid artificial self-interference.

### 5. Real mobility input

The project supports the external **AMOVFLY** real UAV telemetry dataset through `src/mobility/amovfly.py`. Original trajectories are measured mobility data; synchronized/interpolated positions are derived; RF values generated from them are simulated/model-derived.

AMOVFLY data are not redistributed by this repository because a top-level license file was not found during source inspection.

### 6. Resource-allocation research abstraction

Random resource assignment is compared against an experimental distance/interference-aware greedy algorithm. These are system-level research abstractions, **not** normative implementations of NR Sidelink Mode 1 or Mode 2.

### 7. Multi-hop routing

NetworkX helpers support minimum-hop and link-quality-aware path selection on explicitly constructed link graphs.

### 8. Beamforming sensitivity

Directional gain is treated as an explicit experimental sweep. This isolates possible SINR improvement without pretending to implement a complete array/beam-management PHY.

## Main experiments

```bash
# Measurement-derived two-UAV baseline
python -m src.measured_a2a_baseline

# FSPL vs measured A2A vs 3GPP aerial large-scale path loss
python -m simulations.channel_comparison

# 100-seed swarm-density Monte Carlo experiment
python -m simulations.density_measurement_based

# Resource-allocation abstraction study
python -m simulations.resource_allocation_study

# Multi-hop routing study
python -m simulations.routing_study

# Beamforming-gain sensitivity
python -m simulations.beamforming_sensitivity
```

For a real AMOVFLY pair, see `docs/experiments/004_real_mobility_amovfly.md`.

## Validation

Install dependencies and run:

```bash
pip install -r requirements.txt
pytest -q
```

GitHub Actions also runs the unit tests and baseline smoke checks. See `docs/experiments/006_validation_status.md` for the exact implemented boundary.

## Repository structure

```text
uav-sidelink-swarm/
├── .github/workflows/
├── config/
├── data/
├── docs/experiments/
├── figures/
├── references/
│   ├── parameter_sources.md
│   └── references.bib
├── results/
├── simulations/
├── src/
│   ├── antenna/
│   ├── channel_models/
│   ├── mobility/
│   ├── networking/
│   └── sidelink/
└── tests/
```

## Important limitations

The current repository does **not** claim to implement:

- a bit-accurate NR Sidelink PHY;
- actual NR MCS/LDPC/BLER curves;
- HARQ procedures;
- a normative Mode-1/Mode-2 scheduler;
- full 3GPP fast fading;
- full MIMO/beam management;
- measured multi-UAV RF interference or measured PDR.

Until an MCS/BLER link model is sourced and validated, `link_success_proxy` remains an SINR-threshold proxy. `B*log2(1+SINR)` remains a Shannon theoretical upper bound, not NR user throughput.

## Core references

- A. Giannakoulas et al., **“Sidelink Communication for Unmanned Platforms' (UxU) Swarms in Challenging Scenarios,”** CIEES 2025, DOI `10.1109/CIEES66347.2025.11300255`.
- U. Erdemir et al., IEEE VTC 2023-Spring, DOI `10.1109/VTC2023-Spring57618.2023.10199853`.
- 3GPP TR 38.901 V19.4.0, Release 19.
- 3GPP TR 36.777, aerial-vehicle channel-model annexes.
- 3GPP TS 38.214 / TS 38.213 V19.4.0 for NR physical-layer procedure background.

Detailed parameter provenance is maintained in `references/parameter_sources.md`.
