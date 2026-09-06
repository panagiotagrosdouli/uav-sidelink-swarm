# Experiment 004 — Real AMOVFLY simultaneous-flight mobility

## Objective

Use a publicly available simultaneous AMOVFLY UAV pair as measured mobility input and derive a physically safe common-frame horizontal separation time series.

## Dataset and provenance

AMOVFLY (`YujiaoHu/AMOVFLY-Dataset`) is used strictly as a mobility/telemetry dataset, not as a sidelink RF measurement dataset. The public `Multi-Uav_infosheet.csv` identifies the following simultaneous pair:

- `UavY_P0A10S6_1`, takeoff metadata `2024/11/21 13:50`;
- `UavR_P0A40VarS8_1`, takeoff metadata `2024/11/21 13:46`.

The ready CSVs expose `real_lat`/`real_long` geodetic coordinates and local `gps_x/gps_y/gps_z`. The local coordinates are not assumed to share a cross-aircraft origin.

The repository does not vendor the raw AMOVFLY CSVs. The dedicated workflow downloads them directly from the public source for reproducible execution.

## Processing classification

- source telemetry: `MEASURED_DATASET`;
- geodetic-to-common-frame transformation: `DERIVED_FROM_MEASURED_DATASET`;
- synchronization/interpolation: `DERIVED_FROM_MEASURED_DATASET`;
- horizontal UAV separation: `DERIVED_FROM_MEASURED_DATASET`;
- RF metrics generated in the canonical public-pair run: **false**.

## Why the canonical result is 2D horizontal separation

The public ready files used here do not expose a verified common absolute-altitude field. Therefore the experiment does not reconstruct a 3D UAV-to-UAV distance from unrelated local vertical coordinates and does not apply path-loss/SINR/BLER/goodput models to an unsupported 3D geometry.

Both aircraft are transformed using their public latitude/longitude samples into a common WGS84-derived horizontal frame. The vertical component is explicitly excluded from the reported separation.

## Reproduction

The dedicated GitHub Actions workflow downloads and runs the pair automatically. Equivalent local execution is:

```bash
python -m simulations.real_mobility_pair \
  --uav1-file /path/to/UavY_P0A10S6_1.csv \
  --uav1-time "2024/11/21 13:50" \
  --uav2-file /path/to/UavR_P0A40VarS8_1.csv \
  --uav2-time "2024/11/21 13:46"
```

## Canonical validated output

Canonical PR-head workflow run: `34033702695` (`amovfly-public-pair`, run #2), head commit `2fda9e428fddaac8408a1dce20989d8f58055a61`.

Artifact:

- ID: `9989459870`;
- digest: `sha256:90f8b22742d92f125a7f3f51571dc70437e6ae035f0de6cb9627c477fa105d14`;
- synchronized samples: `1831`;
- overlapping duration: `366.000087 s`;
- horizontal separation min: `2.057230 m`;
- horizontal separation mean: `43.865579 m`;
- horizontal separation max: `127.751559 m`;
- coordinate frame: `COMMON_ENU_WGS84_HORIZONTAL_ONLY`;
- distance dimension: `2D_HORIZONTAL`;
- all separation values finite and non-negative: yes.

Outputs include:

- `results/real_mobility_pair/aligned_pair_mobility.csv`;
- `results/real_mobility_pair/provenance.csv`;
- `figures/mobility/real_pair_distance_vs_time.png`;
- `figures/mobility/real_pair_distance_vs_time.pdf`.

## Scientific non-claims

This experiment does **not** provide measured RF performance, measured PDR, measured latency, measured sidelink throughput, 3D A2A separation, or model-derived RF values for the public pair. Any later RF study requires a separately justified common 3D trajectory.
