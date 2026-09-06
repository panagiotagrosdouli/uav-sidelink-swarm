"""Extract 5G-LENA Table-1 SINR/BLER tuples from a local nr-eesm-t1.cc file.

The project intentionally does not vendor the upstream GPL-2.0-only C++ source.
Obtain an official 5G-LENA checkout and run this parser locally. The generated
numbers remain LINK_LEVEL_SIMULATION data, not measurements and not 3GPP BLER
curves.

The parser extracts every available MCS/CBS curve in both BG TYPE 1 and BG TYPE
2 blocks of BlerForSinr1 and records upstream provenance metadata in the output.
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
BG_RE = re.compile(r"\{\s*//\s*BG TYPE\s+(\d+)")

OUTPUT_FIELDS = [
    "mcs_index",
    "base_graph",
    "code_block_size",
    "sinr_db",
    "bler",
    "source_file",
    "source_version",
    "source_commit",
    "source_classification",
]


def _numbers(text: str) -> list[float]:
    return [float(x) for x in NUMBER_RE.findall(text)]


def _table1_block(source: str) -> str:
    marker = "BlerForSinr1"
    start = source.find(marker)
    if start < 0:
        raise ValueError("BlerForSinr1 block not found")
    # Stop before the constructor/next top-level section if possible. Parsing is
    # additionally constrained by explicit BG markers, so a conservative tail is OK.
    return source[start:]


def _extract_bg(block: str, base_graph: int) -> list[dict[str, float | int]]:
    matches = list(BG_RE.finditer(block))
    target_index = next((i for i, m in enumerate(matches) if int(m.group(1)) == base_graph), None)
    if target_index is None:
        raise ValueError(f"BG TYPE {base_graph} block not found")
    start = matches[target_index].end()
    end = matches[target_index + 1].start() if target_index + 1 < len(matches) else len(block)
    bg_block = block[start:end]

    rows: list[dict[str, float | int]] = []
    mcs_matches = list(MCS_RE.finditer(bg_block))
    for idx, match in enumerate(mcs_matches):
        mcs = int(match.group(1))
        section_end = mcs_matches[idx + 1].start() if idx + 1 < len(mcs_matches) else len(bg_block)
        section = bg_block[match.end():section_end]
        cbs_matches = list(CBS_RE.finditer(section))
        for c_idx, cbs_match in enumerate(cbs_matches):
            cbs = int(cbs_match.group(1))
            if cbs != int(cbs_match.group(2)):
                raise ValueError(f"inconsistent CBS annotation for MCS {mcs}: {cbs_match.groups()}")
            c_end = cbs_matches[c_idx + 1].start() if c_idx + 1 < len(cbs_matches) else len(section)
            tail = section[cbs_match.end():c_end]
            arrays = ARRAY_RE.findall(tail)
            numeric_arrays = [_numbers(a) for a in arrays]
            numeric_arrays = [a for a in numeric_arrays if len(a) >= 2]
            if len(numeric_arrays) < 2:
                continue
            sinr, bler = numeric_arrays[0], numeric_arrays[1]
            if len(sinr) != len(bler):
                raise ValueError(f"SINR/BLER length mismatch for BG{base_graph} MCS{mcs} CBS{cbs}")
            if any(b < 0.0 or b > 1.0 for b in bler):
                raise ValueError(f"invalid BLER for BG{base_graph} MCS{mcs} CBS{cbs}")
            if any(b <= a for a, b in zip(sinr, sinr[1:])):
                raise ValueError(f"non-increasing SINR grid for BG{base_graph} MCS{mcs} CBS{cbs}")
            for s, b in zip(sinr, bler):
                rows.append({
                    "mcs_index": mcs,
                    "base_graph": base_graph,
                    "code_block_size": cbs,
                    "sinr_db": s,
                    "bler": b,
                })
    return rows


def extract_table1(source: str) -> list[dict[str, float | int]]:
    """Extract every available Table-1 BG1/BG2 SINR-BLER point."""
    block = _table1_block(source)
    rows: list[dict[str, float | int]] = []
    for bg in (1, 2):
        rows.extend(_extract_bg(block, bg))
    if not rows:
        raise ValueError("no Table-1 BLER points extracted")
    return rows


def extract_table1_bg1(source: str) -> list[dict[str, float | int]]:
    """Backward-compatible BG1-only helper used by older callers/tests."""
    return _extract_bg(_table1_block(source), 1)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path, help="local nr-eesm-t1.cc path")
    parser.add_argument("output", type=Path, help="output CSV path")
    parser.add_argument("--source-version", default="unknown", help="5G-LENA release/tag, e.g. v5.0")
    parser.add_argument("--source-commit", default="unknown", help="upstream Git commit SHA")
    args = parser.parse_args()

    rows = extract_table1(args.source.read_text(encoding="utf-8"))
    enriched = []
    for row in rows:
        enriched.append({
            **row,
            "source_file": args.source.name,
            "source_version": args.source_version,
            "source_commit": args.source_commit,
            "source_classification": "LINK_LEVEL_SIMULATION",
        })

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(enriched)
    n_curves = len({(r["base_graph"], r["mcs_index"], r["code_block_size"]) for r in rows})
    print(f"Extracted {len(rows)} points across {n_curves} curves to {args.output}")


if __name__ == "__main__":
    main()
