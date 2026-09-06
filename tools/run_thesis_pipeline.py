"""Run the reproducible thesis experiment suite and record status/manifest."""
from __future__ import annotations

import csv
import subprocess
import sys
from pathlib import Path

from src.reproducibility import write_manifest

EXPERIMENTS = [
    ("measured_a2a_baseline", [sys.executable, "-m", "src.measured_a2a_baseline"], "MEASUREMENT_DERIVED_PROPAGATION"),
    ("channel_comparison", [sys.executable, "-m", "simulations.channel_comparison"], "DERIVED_MODEL_COMPARISON"),
    ("density_measurement_based", [sys.executable, "-m", "simulations.density_measurement_based"], "SYNTHETIC_GEOMETRY_WITH_MEASUREMENT_DERIVED_CHANNEL"),
    ("resource_allocation_study", [sys.executable, "-m", "simulations.resource_allocation_study"], "THIS_WORK_SYSTEM_LEVEL_ABSTRACTION"),
    ("routing_study", [sys.executable, "-m", "simulations.routing_study"], "THIS_WORK_SYSTEM_LEVEL_ABSTRACTION"),
    ("beamforming_sensitivity", [sys.executable, "-m", "simulations.beamforming_sensitivity"], "EXPERIMENTAL_SWEEP"),
    ("nr_link_performance", [sys.executable, "-m", "simulations.nr_link_performance_study"], "STANDARD_PLUS_LINK_LEVEL_SIMULATION_DERIVED"),
    ("harq_tbs_latency", [sys.executable, "-m", "simulations.harq_tbs_latency_study"], "STANDARD_PLUS_DERIVED_HARQ_ABSTRACTION"),
    ("sidelink_overhead_sensitivity", [sys.executable, "-m", "simulations.sidelink_overhead_sensitivity"], "EXPERIMENTAL_CONFIGURATION_SWEEP"),
]


def main() -> int:
    out = Path("results/reproducibility")
    out.mkdir(parents=True, exist_ok=True)
    records: list[dict[str, object]] = []
    failed = False

    for name, command, classification in EXPERIMENTS:
        proc = subprocess.run(command, text=True, capture_output=True)
        record = {
            "name": name,
            "command": " ".join(command),
            "classification": classification,
            "returncode": proc.returncode,
            "status": "success" if proc.returncode == 0 else "failed",
        }
        records.append(record)
        if proc.returncode != 0:
            failed = True
            print(f"[FAIL] {name}\n{proc.stdout}\n{proc.stderr}", file=sys.stderr)
        else:
            print(f"[OK] {name}")

    with (out / "experiment_status.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["name", "command", "classification", "returncode", "status"])
        writer.writeheader()
        writer.writerows(records)

    write_manifest(out / "run_manifest.json", records)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
