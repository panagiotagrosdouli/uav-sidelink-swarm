"""Fetch and extract the official 5G-LENA v5.0 Table-1 BLER source.

This command deliberately downloads the GPL upstream source at run time rather
than redistributing it.  It writes only the processed numerical table plus
provenance metadata to the requested output path.

Network access is required.  The release/tag is pinned to v5.0 / 47a3adc2.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import urllib.request
from pathlib import Path

from tools.extract_5glena_bler import (
    OFFICIAL_5GLENA_RELEASE_COMMIT,
    OFFICIAL_5GLENA_VERSION,
    OFFICIAL_SOURCE_URL,
    enrich_rows,
    extract_table1,
)


def fetch_source(url: str = OFFICIAL_SOURCE_URL, timeout_s: int = 60) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "uav-sidelink-swarm-research"})
    with urllib.request.urlopen(req, timeout=timeout_s) as response:
        data = response.read()
    text = data.decode("utf-8")
    if "BlerForSinr1" not in text or "BG TYPE 1" not in text or "BG TYPE 2" not in text:
        raise ValueError("downloaded file does not look like the expected 5G-LENA Table-1 source")
    return text


def write_processed_table(source: str, output: str | Path, source_url: str) -> int:
    digest = hashlib.sha256(source.encode("utf-8")).hexdigest()
    rows = enrich_rows(
        extract_table1(source),
        source_version=OFFICIAL_5GLENA_VERSION,
        source_commit=OFFICIAL_5GLENA_RELEASE_COMMIT,
        source_url=source_url,
    )
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0].keys()) + ["source_file_sha256"] if rows else []
    with output.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({**row, "source_file_sha256": digest})
    return len(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "output",
        type=Path,
        nargs="?",
        default=Path("data/generated/5glena_v5_table1_full.csv"),
    )
    parser.add_argument("--url", default=OFFICIAL_SOURCE_URL)
    args = parser.parse_args()
    source = fetch_source(args.url)
    count = write_processed_table(source, args.output, args.url)
    print(
        f"Extracted {count} BLER points from 5G-LENA {OFFICIAL_5GLENA_VERSION} "
        f"({OFFICIAL_5GLENA_RELEASE_COMMIT}) to {args.output}"
    )


if __name__ == "__main__":
    main()
