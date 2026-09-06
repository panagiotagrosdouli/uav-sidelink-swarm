"""Load sourced SINR/BLER points into link-performance curves."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.sidelink.link_performance import BlerCurve


def load_bler_curves(path: str | Path, source: str) -> dict[tuple[int, int, int], BlerCurve]:
    df = pd.read_csv(path)
    required = {"mcs_index", "base_graph", "code_block_size", "sinr_db", "bler"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"BLER CSV missing columns: {sorted(missing)}")

    curves: dict[tuple[int, int, int], BlerCurve] = {}
    for key, group in df.groupby(["mcs_index", "base_graph", "code_block_size"], sort=True):
        mcs, bg, cbs = (int(key[0]), int(key[1]), int(key[2]))
        group = group.sort_values("sinr_db")
        curves[(mcs, bg, cbs)] = BlerCurve(
            mcs_index=mcs,
            base_graph=bg,
            code_block_size=cbs,
            sinr_db=tuple(float(v) for v in group.sinr_db),
            bler=tuple(float(v) for v in group.bler),
            source=source,
        )
    return curves


def curves_for_cbs(
    curves: dict[tuple[int, int, int], BlerCurve],
    code_block_size: int,
    base_graph: int = 1,
) -> list[BlerCurve]:
    selected = [
        curve
        for (mcs, bg, cbs), curve in curves.items()
        if bg == base_graph and cbs == code_block_size
    ]
    return sorted(selected, key=lambda c: c.mcs_index)
