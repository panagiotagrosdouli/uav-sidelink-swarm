"""Quantify the cost of explicit sidelink control/reference-signal overhead.

This study intentionally varies CONFIGURATION choices instead of presenting one
PSCCH/DM-RS pattern as universal. TBS computation itself follows TS 38.214.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.sidelink.resource_grid import SidelinkResourceGrid


def main() -> None:
    rows = []
    for mcs in [4, 5, 6, 10, 14, 20]:
        ideal = SidelinkResourceGrid(
            n_pscch_symbols=0,
            n_guard_symbols=0,
            n_pssch_symbols=14,
            dmrs_re_per_prb=0,
        )
        ideal_tbs = ideal.tbs_bits(mcs)
        for pscch_symbols in [1, 2, 3]:
            for dmrs_re in [12, 24, 36]:
                n_pssch = 14 - pscch_symbols - 1
                grid = SidelinkResourceGrid(
                    n_pscch_symbols=pscch_symbols,
                    n_guard_symbols=1,
                    n_pssch_symbols=n_pssch,
                    dmrs_re_per_prb=dmrs_re,
                )
                tbs = grid.tbs_bits(mcs)
                rows.append({
                    "mcs_index": mcs,
                    "pscch_symbols": pscch_symbols,
                    "guard_symbols": 1,
                    "pssch_symbols": n_pssch,
                    "dmrs_re_per_prb": dmrs_re,
                    "usable_re_per_prb": grid.usable_re_per_prb,
                    "tbs_bits": tbs,
                    "ideal_zero_overhead_tbs_bits": ideal_tbs,
                    "tbs_loss_fraction_vs_ideal": 1.0 - tbs / ideal_tbs,
                    "slot_duration_ms": grid.slot_duration_ms,
                })

    df = pd.DataFrame(rows)
    out = Path("results/sidelink_overhead")
    out.mkdir(parents=True, exist_ok=True)
    df.to_csv(out / "sensitivity.csv", index=False)
    summary = df.groupby("mcs_index").agg(
        min_tbs_bits=("tbs_bits", "min"),
        max_tbs_bits=("tbs_bits", "max"),
        mean_tbs_loss_fraction_vs_ideal=("tbs_loss_fraction_vs_ideal", "mean"),
    ).reset_index()
    summary.to_csv(out / "summary.csv", index=False)
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
