"""Reproducibility metadata for thesis experiments."""
from __future__ import annotations

import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

TRACKED_PACKAGES = ("numpy", "pandas", "matplotlib", "PyYAML", "pytest", "networkx")


def git_sha() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def package_versions() -> dict[str, str | None]:
    out: dict[str, str | None] = {}
    for name in TRACKED_PACKAGES:
        try:
            out[name] = version(name)
        except PackageNotFoundError:
            out[name] = None
    return out


def build_manifest(experiments: list[dict[str, object]]) -> dict[str, object]:
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "git_sha": git_sha(),
        "python_version": sys.version.split()[0],
        "platform": platform.platform(),
        "package_versions": package_versions(),
        "scientific_policy": {
            "source_chain": "SOURCE -> MODEL -> IMPLEMENTATION -> VALIDATION -> EXPERIMENT -> RESULT -> INTERPRETATION -> LIMITATIONS",
            "allowed_classifications": [
                "MEASURED",
                "MEASURED_DATASET",
                "STANDARD",
                "LITERATURE",
                "LINK_LEVEL_SIMULATION",
                "DERIVED",
                "EXPERIMENTAL_SWEEP",
                "EXPERIMENTAL_ASSUMPTION",
                "SYNTHETIC",
            ],
        },
        "experiments": experiments,
    }


def write_manifest(path: str | Path, experiments: list[dict[str, object]]) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(build_manifest(experiments), indent=2) + "\n", encoding="utf-8")
    return target
