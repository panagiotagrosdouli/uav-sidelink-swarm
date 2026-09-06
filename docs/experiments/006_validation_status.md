# Validation status

## Implemented and unit-tested

- measurement-derived A2A log-distance path loss;
- FSPL reference;
- restricted equal-height 3GPP Release-19 Case-9 UMi-AV large-scale helpers;
- dBm/W conversions and thermal-noise calculation;
- half-duplex disjoint Tx/Rx pairing;
- deterministic snapshot reproducibility;
- AMOVFLY trajectory synchronization logic;
- random/greedy resource-assignment helpers;
- graph-routing helpers.

## Reproducible simulation scripts

- `src.measured_a2a_baseline`
- `simulations.channel_comparison`
- `simulations.density_measurement_based`
- `simulations.resource_allocation_study`
- `simulations.routing_study`
- `simulations.beamforming_sensitivity`

A real-mobility script is provided, but it requires external AMOVFLY files and a validated common coordinate frame before final thesis interpretation.

## Not yet scientifically complete

The repository intentionally does not claim completion of:

- bit-accurate NR Sidelink PHY;
- modulation/coding/LDPC implementation;
- MCS-to-BLER link curves;
- HARQ;
- normative Mode-1/Mode-2 sensing/resource selection;
- complete 3GPP fast fading;
- real measured swarm RF interference;
- full antenna array / MIMO / beam management;
- experimentally measured PDR or latency.

These require additional authoritative link-level sources or dedicated PHY simulation and should not be inferred from the current system-level outputs.
