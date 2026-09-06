# Experiment 004 — Real AMOVFLY mobility with model-derived RF link values

## Objective

Use measured multi-UAV flight trajectories as the mobility input, then evaluate UAV-to-UAV distance and a measurement-derived A2A propagation model over time.

## Dataset

AMOVFLY (`YujiaoHu/AMOVFLY-Dataset`) reports 270+ flights and more than 46 hours of telemetry from three UAVs. The multi-UAV information sheet identifies simultaneous flight pairs. Ready-data CSVs contain time, local x/y/z position, geographic coordinates, velocity, wind and other telemetry.

AMOVFLY is a **mobility/telemetry dataset**, not a sidelink RF measurement dataset.

No dataset files are redistributed by this repository because a top-level license file was not found during repository inspection. Obtain the data directly from the original source.

## Processing classification

- original `time`, `gps_x`, `gps_y`, `gps_z`: `MEASURED_DATASET`;
- synchronization/interpolation: `DERIVED_FROM_MEASURED_DATASET`;
- A2A distance calculated from synchronized positions: `DERIVED_FROM_MEASURED_DATASET`;
- path loss / received power generated with the Erdemir fit: `SIMULATION_USING_MEASUREMENT_DERIVED_CHANNEL`.

## Example pair

The AMOVFLY multi-UAV metadata includes, among others, a simultaneous pair:

- `UavY_P0A10S6_1`, takeoff metadata `2024/11/21 13:50`;
- `UavR_P0A40VarS8_1`, takeoff metadata `2024/11/21 13:46`.

The exact ready-data paths depend on the scenario folders in the external dataset.

## Reproduction

```bash
python -m simulations.real_mobility_pair \
  --uav1-file /path/to/UavY_P0A10S6_1.csv \
  --uav1-time "2024/11/21 13:50" \
  --uav2-file /path/to/UavR_P0A40VarS8_1.csv \
  --uav2-time "2024/11/21 13:46"
```

## Outputs

- synchronized real trajectories and derived A2A distances;
- model-derived path loss and received power;
- distance-vs-time plot;
- model-derived received-power-vs-time plot.

## Important limitation

Different AMOVFLY UAVs may use local coordinate frames tied to their own takeoff points. Before interpreting direct Euclidean distance from `gps_x/y/z` as physically exact separation, validate whether the paired files share a common local reference. If they do not, transform the reported global latitude/longitude/altitude fields into a common coordinate frame first. This validation is required before final thesis use.
