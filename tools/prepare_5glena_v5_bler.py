"""Prepare complete 5G-LENA v5.0 Table-1 BLER data from official CTTC source.

This utility downloads (or accepts a local copy of) the GPL-2.0-only upstream
`model/nr-eesm-t1.cc`, records its SHA-256, and writes a processed numerical CSV
using `tools.extract_5glena_bler`. The upstream C++ source is NOT intended to be
committed to this repository.

The resulting CSV is LINK_LEVEL_SIMULATION data. It is not a 3GPP BLER table and
not measured UAV RF data.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
import urllib.request
from pathlib import Path

from tools.extract_5glena_bler import OUTPUT_FIELDS, extract_table1
import csv

OFFICIAL_VERSION = "v5.0"
OFFICIAL_RELEASE_COMMIT_SHORT = "47a3adc2"
OFFICIAL_RELEASE_DOI = "10.5281/zenodo.21165297"
OFFICIAL_SOURCE_URL = "https://gitlab.com/cttc-lena/nr/-/raw/v5.0/model/nr-eesm-t1.cc"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def download_source(destination: Path) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(OFFICIAL_SOURCE_URL, headers={"User-Agent": "uav-sidelink-swarm-research"})
    with urllib.request.urlopen(request, timeout=60) as response, destination.open("wb") as out:
        out.write(response.read())
    return destination


def prepare(source: Path, output: Path, manifest: Path) -> tuple[int, int]:
    text = source.read_text(encoding="utf-8")
    rows = extract_table1(text)
    enriched = [{
        **row,
        "source_file": "nr-eesm-t1.cc",
        "source_version": OFFICIAL_VERSION,
        "source_commit": OFFICIAL_RELEASE_COMMIT_SHORT,
        "source_classification": "LINK_LEVEL_SIMULATION",
    } for row in rows]
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(enriched)
    curves = {(r["base_graph"], r["mcs_index"], r["code_block_size"]) for r in rows}
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(json.dumps({
        "source_url": OFFICIAL_SOURCE_URL,
        "source_version": OFFICIAL_VERSION,
        "release_commit_short": OFFICIAL_RELEASE_COMMIT_SHORT,
        "release_doi": OFFICIAL_RELEASE_DOI,
        "source_sha256": sha256_file(source),
        "source_license": "GPL-2.0-only",
        "processed_data_classification": "LINK_LEVEL_SIMULATION",
        "points": len(rows),
        "curves": len(curves),
        "base_graphs": sorted({int(r["base_graph"]) for r in rows}),
        "mcs_indices": sorted({int(r["mcs_index"]) for r in rows}),
        "note": "Processed numerical data generated locally from official CTTC 5G-LENA source; upstream C++ source is not vendored.",
    }, indent=2) + "\n", encoding="utf-8")
    return len(rows), len(curves)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, help="local official v5.0 nr-eesm-t1.cc; omit to download transiently")
    parser.add_argument("--output", type=Path, default=Path("data/generated/5glena_v5_table1_bler.csv"))
    parser.add_argument("--manifest", type=Path, default=Path("data/generated/5glena_v5_table1_bler_manifest.json"))
    args = parser.parse_args()

    if args.source:
        points, curves = prepare(args.source, args.output, args.manifest)
    else:
        with tempfile.TemporaryDirectory(prefix="5glena-v5-") as tmp:
            source = download_source(Path(tmp) / "nr-eesm-t1.cc")
            points, curves = prepare(source, args.output, args.manifest)
    print(f"Prepared {points} BLER points across {curves} curves from official 5G-LENA {OFFICIAL_VERSION}.")
    print(f"CSV: {args.output}")
    print(f"Manifest: {args.manifest}")


if __name__ == "__main__":
    main()
