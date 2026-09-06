"""Extract 5G-LENA Table-1 SINR/BLER tuples from a local nr-eesm-t1.cc file.

This tool intentionally does not vendor the upstream GPL-2.0-only C++ source.
Obtain the source from the official 5G-LENA project, then run this parser to
produce a CSV for local research use. The output is numerical link-level
simulation data and must remain labelled LINK_LEVEL_SIMULATION.
"""
from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path

MCS_RE = re.compile(r"//\s*MCS\s+(\d+)")
CBS_RE = re.compile(r"\{(\d+)U,\s*//\s*SINR and BLER for CBS\s+(\d+)")
ARRAY_RE = re.compile(r"\{([^{}]+)\}")
NUMBER_RE = re.compile(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?")


def _numbers(text: str) -> list[float]:
    return [float(x) for x in NUMBER_RE.findall(text)]


def extract_table1_bg1(source: str) -> list[dict[str, float | int]]:
    """Best-effort parser for the first (BG1) 5G-LENA BlerForSinr1 block."""
    bg1_start = source.find("{ // BG TYPE 1")
    bg2_start = source.find("{ // BG TYPE 2")
    if bg1_start < 0:
        raise ValueError("BG TYPE 1 block not found")
    block = source[bg1_start : bg2_start if bg2_start > bg1_start else len(source)]

    rows: list[dict[str, float | int]] = []
    mcs_matches = list(MCS_RE.finditer(block))
    for idx, match in enumerate(mcs_matches):
        mcs = int(match.group(1))
        section_end = mcs_matches[idx + 1].start() if idx + 1 < len(mcs_matches) else len(block)
        section = block[match.end() : section_end]
        for cbs_match in CBS_RE.finditer(section):
            cbs = int(cbs_match.group(1))
            tail = section[cbs_match.end() :]
            arrays = ARRAY_RE.findall(tail)
            numeric_arrays = [_numbers(a) for a in arrays]
            numeric_arrays = [a for a in numeric_arrays if len(a) >= 2]
            if len(numeric_arrays) < 2:
                continue
            sinr, bler = numeric_arrays[0], numeric_arrays[1]
            if len(sinr) != len(bler):
                continue
            for s, b in zip(sinr, bler):
                rows.append({
                    "mcs_index": mcs,
                    "base_graph": 1,
                    "code_block_size": cbs,
                    "sinr_db": s,
                    "bler": b,
                })
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path, help="local nr-eesm-t1.cc path")
    parser.add_argument("output", type=Path, help="output CSV path")
    args = parser.parse_args()

    rows = extract_table1_bg1(args.source.read_text(encoding="utf-8"))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["mcs_index", "base_graph", "code_block_size", "sinr_db", "bler"],
        )
        writer.writeheader()
        writer.writerows(rows)
    print(f"Extracted {len(rows)} SINR/BLER points to {args.output}")


if __name__ == "__main__":
    main()
