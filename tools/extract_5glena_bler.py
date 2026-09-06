"""Extract 5G-LENA Table-1 SINR/BLER tuples from ``nr-eesm-t1.cc``.

The upstream C++ source is GPL-2.0-only and is intentionally not vendored by
this repository.  The parser can consume an explicitly downloaded source file
and emits numerical link-level-simulation data with source metadata.

Scientific classification of emitted BLER values: LINK_LEVEL_SIMULATION.
They are not 3GPP-standard curves and are not UAV RF measurements.
"""
from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path

from src.sidelink.nr_mcs import get_mcs

OFFICIAL_5GLENA_VERSION = "v5.0"
OFFICIAL_5GLENA_RELEASE_COMMIT = "47a3adc2"
OFFICIAL_SOURCE_URL = (
    "https://gitlab.com/cttc-lena/nr/-/raw/v5.0/model/nr-eesm-t1.cc"
)

MCS_RE = re.compile(r"//\s*MCS\s+(\d+)")
CBS_RE = re.compile(r"\{(\d+)U,\s*//\s*SINR and BLER for CBS\s+(\d+)")
ARRAY_RE = re.compile(r"\{([^{}]+)\}")
NUMBER_RE = re.compile(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?")


def _numbers(text: str) -> list[float]:
    return [float(x) for x in NUMBER_RE.findall(text)]


def _bg_block(source: str, base_graph: int) -> str:
    marker = f"{{ // BG TYPE {base_graph}"
    start = source.find(marker)
    if start < 0:
        raise ValueError(f"BG TYPE {base_graph} block not found")
    if base_graph == 1:
        end = source.find("{ // BG TYPE 2", start + len(marker))
        return source[start : end if end >= 0 else len(source)]
    return source[start:]


def _extract_bg(source: str, base_graph: int) -> list[dict[str, float | int]]:
    block = _bg_block(source, base_graph)
    rows: list[dict[str, float | int]] = []
    mcs_matches = list(MCS_RE.finditer(block))
    for idx, match in enumerate(mcs_matches):
        mcs = int(match.group(1))
        section_end = mcs_matches[idx + 1].start() if idx + 1 < len(mcs_matches) else len(block)
        section = block[match.end() : section_end]
        cbs_matches = list(CBS_RE.finditer(section))
        for cidx, cbs_match in enumerate(cbs_matches):
            # The source repeats the CBS value in the key and in the comment.
            cbs_key = int(cbs_match.group(1))
            cbs_comment = int(cbs_match.group(2))
            if cbs_key != cbs_comment:
                raise ValueError(
                    f"CBS key/comment mismatch for MCS {mcs}, BG{base_graph}: "
                    f"{cbs_key} != {cbs_comment}"
                )
            entry_end = cbs_matches[cidx + 1].start() if cidx + 1 < len(cbs_matches) else len(section)
            entry = section[cbs_match.end() : entry_end]
            arrays = [_numbers(a) for a in ARRAY_RE.findall(entry)]
            numeric_arrays = [a for a in arrays if len(a) >= 2]
            if len(numeric_arrays) < 2:
                continue
            sinr, bler = numeric_arrays[0], numeric_arrays[1]
            if len(sinr) != len(bler):
                raise ValueError(
                    f"SINR/BLER length mismatch for MCS {mcs}, BG{base_graph}, CBS {cbs_key}"
                )
            for s, b in zip(sinr, bler):
                if not 0.0 <= b <= 1.0:
                    raise ValueError(
                        f"BLER outside [0,1] for MCS {mcs}, BG{base_graph}, CBS {cbs_key}"
                    )
                rows.append(
                    {
                        "mcs_index": mcs,
                        "base_graph": base_graph,
                        "code_block_size": cbs_key,
                        "sinr_db": s,
                        "bler": b,
                    }
                )
    return rows


def extract_table1(source: str) -> list[dict[str, float | int]]:
    """Extract every populated Table-1 curve from both LDPC base graphs."""
    rows = _extract_bg(source, 1) + _extract_bg(source, 2)
    rows.sort(
        key=lambda r: (
            int(r["base_graph"]),
            int(r["mcs_index"]),
            int(r["code_block_size"]),
            float(r["sinr_db"]),
        )
    )
    return rows


def extract_table1_bg1(source: str) -> list[dict[str, float | int]]:
    """Backward-compatible helper returning only BG1 curves."""
    return _extract_bg(source, 1)


def enrich_rows(
    rows: list[dict[str, float | int]],
    *,
    source_version: str,
    source_commit: str,
    source_url: str,
) -> list[dict[str, float | int | str]]:
    """Attach STANDARD MCS metadata and explicit upstream provenance."""
    out: list[dict[str, float | int | str]] = []
    for row in rows:
        mcs = get_mcs(int(row["mcs_index"]))
        out.append(
            {
                **row,
                "modulation_order": mcs.modulation_order,
                "target_code_rate_x1024": mcs.target_code_rate_x1024,
                "spectral_efficiency": mcs.spectral_efficiency,
                "source_version": source_version,
                "source_commit": source_commit,
                "source_url": source_url,
                "source_classification": "LINK_LEVEL_SIMULATION",
            }
        )
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path, help="local nr-eesm-t1.cc path")
    parser.add_argument("output", type=Path, help="output CSV path")
    parser.add_argument("--source-version", default=OFFICIAL_5GLENA_VERSION)
    parser.add_argument("--source-commit", default=OFFICIAL_5GLENA_RELEASE_COMMIT)
    parser.add_argument("--source-url", default=OFFICIAL_SOURCE_URL)
    args = parser.parse_args()

    rows = enrich_rows(
        extract_table1(args.source.read_text(encoding="utf-8")),
        source_version=args.source_version,
        source_commit=args.source_commit,
        source_url=args.source_url,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "mcs_index",
        "base_graph",
        "code_block_size",
        "sinr_db",
        "bler",
        "modulation_order",
        "target_code_rate_x1024",
        "spectral_efficiency",
        "source_version",
        "source_commit",
        "source_url",
        "source_classification",
    ]
    with args.output.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Extracted {len(rows)} Table-1 SINR/BLER points to {args.output}")


if __name__ == "__main__":
    main()
