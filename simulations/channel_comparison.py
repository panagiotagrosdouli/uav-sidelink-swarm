"""Generate path-loss comparison data/figure for FSPL, measured A2A, and 3GPP UMi-AV LOS."""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.channel_models.free_space import path_loss_db as fspl_db
from src.channel_models.measured_a2a import path_loss_db as measured_db
from src.channel_models.tr38901_a2a import umi_av_los_path_loss_db


def main() -> None:
    carrier_ghz = 3.5
    altitude_m = 100.0
    distances_m = np.geomspace(10.0, 2000.0, 300)

    df = pd.DataFrame({
        "distance_m": distances_m,
        "fspl_db": fspl_db(distances_m, carrier_ghz * 1e9),
        "measured_a2a_fit_db": measured_db(distances_m),
        "tr38901_case9_umi_av_los_db": umi_av_los_path_loss_db(distances_m, altitude_m, carrier_ghz),
    })

    results_dir = Path("results/channel_comparison")
    figures_dir = Path("figures/pathloss")
    results_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)
    df.to_csv(results_dir / "pathloss_comparison.csv", index=False)

    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    ax.semilogx(df.distance_m, df.fspl_db, label="FSPL")
    ax.semilogx(df.distance_m, df.measured_a2a_fit_db, label="Measured A2A fit")
    ax.semilogx(df.distance_m, df.tr38901_case9_umi_av_los_db, label="3GPP Case 9 UMi-AV LOS")
    ax.set_xlabel("UAV-to-UAV distance [m]")
    ax.set_ylabel("Path loss [dB]")
    ax.set_title("A2A path-loss model comparison at 3.5 GHz, h = 100 m")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(figures_dir / "pathloss_comparison.png", dpi=300)
    fig.savefig(figures_dir / "pathloss_comparison.pdf")
    plt.close(fig)


if __name__ == "__main__":
    main()
