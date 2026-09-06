# Experiment 005 — Resource allocation, routing and beamforming sensitivity

## Purpose

Extend the validated propagation/interference baseline into three system-level research questions without claiming a bit-accurate NR implementation.

## A. Resource allocation

Compare:

- reproducible random assignment of abstract sidelink resources;
- an experimental greedy distance/interference-aware assignment designed in this work.

The algorithms are **research abstractions**, not normative NR Sidelink Mode 1 or Mode 2 implementations. 3GPP TS 38.214 V19.4.0 and TS 38.213 V19.4.0 are standards background for sidelink procedures.

Reproduce with:

```bash
python -m simulations.resource_allocation_study
```

## B. Multi-hop routing

Construct a graph from links that satisfy an explicit link-quality threshold, then compare minimum-hop and quality-aware paths. The first routing experiment uses interference-free link SNR to build topology, so it is a graph/connectivity abstraction rather than a full scheduled multi-hop network.

```bash
python -m simulations.routing_study
```

## C. Beamforming sensitivity

Sweep explicit directional desired-link gain assumptions (0/3/6/9 dB) while leaving interference unchanged. This isolates the sensitivity of SINR to directional gain.

The gain values are `EXPERIMENTAL_SWEEP`; they are not claimed as measured antenna gains or as a full MIMO/beam-management implementation.

```bash
python -m simulations.beamforming_sensitivity
```

## Final-use warning

Before thesis conclusions are drawn from these extensions:

1. run CI and retain raw outputs;
2. sensitivity-test assumptions;
3. replace the SINR-threshold success proxy with a sourced MCS/BLER mapping if PDR is reported;
4. do not call the resource allocator “Mode 2” unless the exact 3GPP sensing/resource-selection procedure is implemented and validated;
5. do not call the beamforming sensitivity model “MIMO throughput.”
