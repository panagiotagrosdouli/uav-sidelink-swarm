# Data sources

This repository does **not** treat synthetic coordinates as measured flight data.

## AMOVFLY external trajectory dataset

A suitable real-flight mobility source is the public `YujiaoHu/AMOVFLY-Dataset` repository. Its README reports 270+ flights, more than 46 hours of flight-process data, three UAVs, and a multi-UAV subset with simultaneous flights. Ready-data files expose `time`, `gps_x`, `gps_y`, `gps_z`, geographic coordinates, velocity, wind and other telemetry.

Repository: `https://github.com/YujiaoHu/AMOVFLY-Dataset`

### Licensing / redistribution rule

At the time this project was prepared, no top-level `LICENSE` file was found in the AMOVFLY repository through the GitHub API. Therefore this project **does not vendor or redistribute AMOVFLY flight CSVs**. Users should obtain the dataset directly from its source and comply with any terms provided by its authors.

### Expected local layout

After obtaining the dataset, keep the original files unchanged under a local path outside version control, for example:

```text
data/raw/amovfly/
├── Multi-Uav_infosheet.csv
├── Flight_info.csv
├── FAFS/
├── FAVS/
├── VAFS/
├── VAVS/
└── Random/
```

Raw data must never be overwritten by preprocessing scripts.

### Provenance classification

- Original AMOVFLY telemetry samples: `MEASURED_DATASET`.
- Synchronized/interpolated trajectories created by this project: `DERIVED_FROM_MEASURED_DATASET`.
- Any synthetic fallback trajectory: `SYNTHETIC`.

The dataset is a mobility/telemetry source, **not an RF sidelink measurement dataset**. Applying an RF channel model to AMOVFLY positions produces simulation/model outputs, not measured radio performance.
