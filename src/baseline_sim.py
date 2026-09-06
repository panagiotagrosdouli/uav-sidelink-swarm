"""Baseline UAV-to-UAV sidelink link-budget simulator.

This is deliberately a transparent first model. UAV geometry is synthetic and
radio assumptions are documented in config/baseline.yaml. It must not be
presented as measured RF data.
"""

from pathlib import Path
import math
import yaml
import numpy as np
import pandas as pd


def fspl_db(distance_m: np.ndarray, carrier_frequency_ghz: float) -> np.ndarray:
    """Free-space path loss: 32.45 + 20log10(d_km) + 20log10(f_MHz)."""
    d_km = np.maximum(distance_m, 1e-3) / 1000.0
    f_mhz = carrier_frequency_ghz * 1000.0
    return 32.45 + 20.0 * np.log10(d_km) + 20.0 * np.log10(f_mhz)


def thermal_noise_dbm(bandwidth_mhz: float, noise_figure_db: float) -> float:
    bandwidth_hz = bandwidth_mhz * 1e6
    return -174.0 + 10.0 * math.log10(bandwidth_hz) + noise_figure_db


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    with open(root / "config" / "baseline.yaml", "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    scenario = cfg["scenario"]
    radio = cfg["radio"]
    threshold = cfg["link"]["sinr_threshold_db"]
    rng = np.random.default_rng(scenario["seed"])

    n = scenario["num_uavs"]
    width, height = scenario["area_m"]
    xyz = np.column_stack([
        rng.uniform(0, width, n),
        rng.uniform(0, height, n),
        np.full(n, scenario["altitude_m"], dtype=float),
    ])

    noise_dbm = thermal_noise_dbm(
        radio["bandwidth_mhz"], radio["receiver_noise_figure_db"]
    )

    rows = []
    for tx in range(n):
        for rx in range(tx + 1, n):
            distance = float(np.linalg.norm(xyz[tx] - xyz[rx]))
            path_loss = float(fspl_db(np.array([distance]), radio["carrier_frequency_ghz"])[0])
            received = (
                radio["tx_power_dbm"]
                + radio["tx_gain_dbi"]
                + radio["rx_gain_dbi"]
                - path_loss
            )
            snr = received - noise_dbm
            rows.append({
                "tx": tx,
                "rx": rx,
                "distance_m": distance,
                "path_loss_db": path_loss,
                "rx_power_dbm": received,
                "snr_db": snr,
                "link_ok": snr >= threshold,
            })

    df = pd.DataFrame(rows)
    out_dir = root / "results"
    out_dir.mkdir(exist_ok=True)
    df.to_csv(out_dir / "baseline_links.csv", index=False)

    print(f"UAVs: {n}")
    print(f"Links evaluated: {len(df)}")
    print(f"Noise power: {noise_dbm:.2f} dBm")
    print(f"Mean distance: {df['distance_m'].mean():.2f} m")
    print(f"Mean SNR: {df['snr_db'].mean():.2f} dB")
    print(f"Link success fraction: {df['link_ok'].mean():.3f}")
    print(f"Saved: {out_dir / 'baseline_links.csv'}")


if __name__ == "__main__":
    main()
