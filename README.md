# UAV Sidelink Swarm

Research-oriented Python system-level simulation project for 5G NR Sidelink communication inside UAV swarms.

## Thesis goal

Study how UAV swarm density and mobility affect UAV-to-UAV link quality, interference, reliability and network connectivity, then evaluate controlled improvements from resource allocation, routing, link adaptation and directional antenna gains.

The scientific pipeline is:

`SOURCE -> MODEL -> IMPLEMENTATION -> VALIDATION -> EXPERIMENT -> RESULT -> INTERPRETATION -> LIMITATIONS`

## Scientific data policy

Every important quantity is classified as one of:

- `MEASURED` / `MEASURED_DATASET`
- `STANDARD`
- `LITERATURE`
- `LINK_LEVEL_SIMULATION`
- `DERIVED`
- `EXPERIMENTAL_SWEEP`
- `EXPERIMENTAL_ASSUMPTION`
- `SYNTHETIC`

Synthetic simulation values are never presented as real measurements.

## Implemented research layers

### 1. Published measurement-derived A2A propagation

Primary peer-reviewed source: U. Erdemir et al., **“Measurement-based Channel Characterization for A2A and A2G Wireless Drone Communication Systems,”** IEEE VTC 2023-Spring, DOI `10.1109/VTC2023-Spring57618.2023.10199853`.

The repository reproduces the reported A2A large-scale fit at 3.5 GHz using `eta=2.166` and `PL0=34.650 dB`. Values generated from this fit are labelled measurement-derived, not raw RF samples.

### 2. 3GPP Release-19 aerial-to-aerial large-scale channel

A deliberately limited and auditable equal-height UMi-AV A2A implementation is included from 3GPP TR 38.901 V19.4.0 Case 9 and the referenced TR 36.777 aerial-UE large-scale models. This is not a full fast-fading implementation.

### 3. Common swarm interference simulator

Pluggable FSPL, measurement-derived A2A and 3GPP aerial large-scale propagation feed a common geometry/power model with desired received power, aggregate co-channel interference, SIR and SINR. Legacy threshold-success and Shannon outputs remain only as explicitly labelled preliminary proxies/reference bounds.

### 4. Density Monte Carlo study

Controlled baseline: `N = 5, 10, 20, 30, 50` UAVs over 100 deterministic seeds. Geometry is synthetic and half-duplex-compatible disjoint Tx/Rx pairs avoid artificial self-interference.

### 5. Real mobility input

`src/mobility/amovfly.py` supports the external AMOVFLY UAV telemetry dataset. Original telemetry is `MEASURED_DATASET`; synchronization/interpolation and RF values generated from trajectories are derived. Dataset CSVs are not redistributed here.

### 6. Resource allocation

Random resource assignment is compared with an experimental distance/interference-aware greedy allocator. These are system-level research abstractions, not normative NR Sidelink Mode 1/Mode 2 implementations.

### 7. Multi-hop routing

NetworkX helpers implement minimum-hop and link-quality-aware path selection on explicitly constructed link graphs.

### 8. Beamforming sensitivity

Directional gain is an explicit experimental sweep, isolating possible SINR improvement without claiming a complete array/MIMO beam-management implementation.

### 9. Standards-based MCS + sourced BLER

`src/sidelink/nr_mcs.py` implements non-reserved NR MCS Table-1 indices `0..28` from 3GPP TS 38.214 V19.4.0. `src/sidelink/link_performance.py` and `src/sidelink/bler_io.py` consume sourced SINR-to-BLER curves. A verified 5G-LENA EESM fixture is included for a limited BG1/CBS/MCS subset; those values are `LINK_LEVEL_SIMULATION`, not UAV measurements.

`src/sidelink/link_adaptation.py` selects the available sourced MCS that maximizes expected PHY goodput. The complete upstream 5G-LENA Table-1 dataset can be extracted from an official local `nr-eesm-t1.cc` with `tools/extract_5glena_bler.py` rather than vendoring the full GPL source.

### 10. TBS + LDPC segmentation

`src/sidelink/nr_tbs.py` implements 3GPP TBS quantization and `src/sidelink/ldpc.py` implements the standards-based BG1/BG2 selection and code-block segmentation rules used by the system-level link model.

### 11. HARQ-aware latency abstraction

`src/sidelink/harq.py` adds an ideal Chase-Combining system-level abstraction. It does not invent an Incremental-Redundancy gain and does not claim to reproduce complete NR/5G-LENA HARQ history processing. Feedback/retransmission timing remains explicitly configuration-dependent.

### 12. Sidelink resource-overhead sensitivity

The resource grid explicitly accounts for control/PSCCH symbols, guard symbols, PSSCH symbols and DM-RS RE overhead. The reference grid is an `EXPERIMENTAL_CONFIGURATION`, and a sensitivity study varies control symbols and DM-RS overhead rather than presenting one configuration as universally mandated by 3GPP.

### 13. Reproducible thesis pipeline

`tools/run_thesis_pipeline.py` runs the implemented research suite and writes an experiment status table plus a machine-readable manifest containing Git SHA, Python/package versions and the scientific classification of every registered experiment.

## Main experiments

```bash
python -m src.measured_a2a_baseline
python -m simulations.channel_comparison
python -m simulations.density_measurement_based
python -m simulations.resource_allocation_study
python -m simulations.routing_study
python -m simulations.beamforming_sensitivity
python -m simulations.nr_link_performance_study
python -m simulations.harq_tbs_latency_study
python -m simulations.sidelink_overhead_sensitivity
```

Run the full registered suite with:

```bash
python -m tools.run_thesis_pipeline
```

Validate only the experiment registry/manifest with:

```bash
python -m tools.run_thesis_pipeline --dry-run
```

For a real AMOVFLY pair, see `docs/experiments/004_real_mobility_amovfly.md`.

## Validation

```bash
pip install -r requirements.txt
python -m pytest -q
```

GitHub Actions runs unit tests and all baseline smoke studies.

## Important limitations

The repository does **not** claim to implement:

- a bit-accurate NR Sidelink PHY;
- the complete 5G-LENA SINR-BLER dataset vendored for all MCS/CBS/base-graph combinations;
- exact standards-complete HARQ IR/CC history processing and PSFCH timing for every resource-pool configuration;
- a normative Mode-1/Mode-2 scheduler;
- full 3GPP fast fading;
- full array/MIMO beam management;
- measured multi-UAV RF interference or measured end-to-end PDR/latency.

Where a sourced BLER curve is available, first-transmission reliability is derived from `1 - BLER(SINR)` rather than the legacy fixed SINR threshold. TBS, LDPC and NR MCS rules can be standards-based while final goodput/latency still remain derived system-level outputs when traffic, resource-pool timing, interference geometry or HARQ abstractions are simulated.

## Core references

- A. Giannakoulas et al., CIEES 2025, DOI `10.1109/CIEES66347.2025.11300255`.
- U. Erdemir et al., IEEE VTC 2023-Spring, DOI `10.1109/VTC2023-Spring57618.2023.10199853`.
- N. Patriciello et al., *Simulation Modelling Practice and Theory* 96 (2019), DOI `10.1016/j.simpat.2019.101933`.
- 5G-LENA v5.0 software archive, DOI `10.5281/zenodo.21165297`.
- 3GPP TR 38.901 V19.4.0 and TR 36.777.
- 3GPP TS 38.211 / 38.212 / 38.213 / 38.214 and TS 38.104, exact versions recorded in project documentation.

Detailed provenance is maintained under `references/` and experiment notes under `docs/experiments/`.
