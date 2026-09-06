# Completion core extensions

## Objective

Close high-priority gaps from the experimental master program before the final multi-factor campaign.

## Implemented

1. **5G-LENA Table-1 importer**
   - extracts BG1 and BG2;
   - extracts every available MCS/CBS curve in the upstream `BlerForSinr1` block;
   - validates SINR ordering and BLER bounds;
   - records source version/commit metadata;
   - does not vendor the upstream GPL C++ source.

2. **AMOVFLY common coordinate frame**
   - prefers measured global longitude/latitude/altitude;
   - converts WGS84 geodetic -> ECEF -> one common ENU frame;
   - explicitly rejects cross-UAV distance from `LOCAL_UNKNOWN_ORIGIN` trajectories;
   - RF metrics remain `SIMULATION_USING_MEASURED_MOBILITY`.

3. **Synthetic geometry/mobility families**
   - uniform, grid, circle, clustered and leader-follower geometry;
   - constant-velocity and formation-translation traces;
   - all are `SYNTHETIC`.

4. **Scaling/activity experiment**
   - fixed 1 km × 1 km area with increasing N;
   - fixed spatial density with area scaled as sqrt(N/density);
   - activity-factor sweep;
   - interference decomposition (I/N, dominant interferer fraction, interferer count);
   - 95% confidence intervals.

5. **Resource allocation**
   - random;
   - existing distance-aware greedy;
   - new weighted conflict-graph allocator;
   - Jain goodput fairness;
   - verified limited 5G-LENA BLER subset used for derived goodput in the bundled baseline.

6. **Routing**
   - direct, minimum-hop, quality-aware and reliability-aware routes;
   - route success = product of per-hop success under explicit independence;
   - nominal per-hop PHY latency is summed; scheduling/queueing are not included.

7. **Directionality**
   - desired-link gain only;
   - interference suppression only;
   - combined gain/suppression;
   - remains `DIRECTIONAL_GAIN_SENSITIVITY`, not full MIMO.

8. **Robustness**
   - channel model;
   - receiver noise figure;
   - transmit power;
   - swarm area;
   - valid 3GPP altitude range;
   - deterministic vs sourced UMi-AV LOS shadow fading.

## Critical scientific boundaries

- The bundled BLER fixture remains limited. The importer now supports the full upstream Table-1 dataset, but the full processed data are not committed because the upstream GPL source is intentionally not vendored and redistribution/licensing must be handled deliberately.
- The resource-allocation algorithms are `THIS_WORK` abstractions, not Mode 2.
- The routing layer is a graph/system abstraction, not an NR routing protocol.
- Noise-figure, activity, geometry, gain and many sensitivity values are experimental choices, not measurements.
- Fast fading remains unimplemented unless a suitable sourced model is introduced.

## Reproduction

Smoke validation:

```bash
python -m tools.run_thesis_pipeline --smoke
```

Full registered campaign:

```bash
python -m tools.run_thesis_pipeline
```
