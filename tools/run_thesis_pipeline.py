"""Run the reproducible thesis experiment suite and record status/manifest."""
from __future__ import annotations

import argparse
import csv
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from src.reproducibility import write_manifest


@dataclass(frozen=True)
class Experiment:
    name: str
    module: str
    classification: str
    supports_smoke: bool = False

    def command(self, smoke: bool = False) -> list[str]:
        command = [sys.executable, "-m", self.module]
        if smoke and self.supports_smoke:
            command.append("--smoke")
        return command


EXPERIMENTS = [
    Experiment("measured_a2a_baseline", "src.measured_a2a_baseline", "MEASUREMENT_DERIVED_PROPAGATION"),
    Experiment("channel_comparison", "simulations.channel_comparison", "DERIVED_MODEL_COMPARISON"),
    Experiment("density_measurement_based", "simulations.density_measurement_based", "SYNTHETIC_GEOMETRY_WITH_MEASUREMENT_DERIVED_CHANNEL"),
    Experiment("scaling_geometry_activity", "simulations.scaling_geometry_activity_study", "SYNTHETIC_PLUS_EXPERIMENTAL_SWEEP", True),
    Experiment("scaling_law_analysis", "simulations.scaling_law_analysis", "DESCRIPTIVE_STATISTICAL_FIT"),
    Experiment("resource_allocation_study", "simulations.resource_allocation_study", "THIS_WORK_SYSTEM_LEVEL_ABSTRACTION"),
    Experiment("routing_study", "simulations.routing_study", "THIS_WORK_PLUS_LINK_LEVEL_SIMULATION_DERIVED", True),
    Experiment("beamforming_sensitivity", "simulations.beamforming_sensitivity", "DIRECTIONAL_GAIN_SENSITIVITY", True),
    Experiment("ula_directionality", "simulations.ula_directionality_study", "PHYSICAL_ARRAY_FACTOR_MODEL", True),
    Experiment("robustness_sensitivity", "simulations.robustness_sensitivity", "STANDARD_MIXED_WITH_EXPERIMENTAL_SWEEP", True),
    Experiment("nr_link_performance", "simulations.nr_link_performance_study", "STANDARD_PLUS_LINK_LEVEL_SIMULATION_DERIVED", True),
    Experiment("harq_tbs_latency", "simulations.harq_tbs_latency_study", "STANDARD_PLUS_DERIVED_HARQ_ABSTRACTION", True),
    Experiment("sidelink_overhead_sensitivity", "simulations.sidelink_overhead_sensitivity", "EXPERIMENTAL_CONFIGURATION_SWEEP"),
    Experiment("traffic_load", "simulations.traffic_load_study", "EXPERIMENTAL_TRAFFIC_PLUS_LINK_LEVEL_SIMULATION_DERIVED", True),
    Experiment("failure_analysis", "simulations.failure_analysis", "DERIVED_FAILURE_DIAGNOSTIC", True),
    Experiment("spatial_diagnostics", "simulations.spatial_diagnostics", "DERIVED_SPATIAL_DIAGNOSTIC", True),
    Experiment("ablation", "simulations.ablation_study", "CROSS_LAYER_SYSTEM_LEVEL_ABLATION", True),
    Experiment("paired_effect_analysis", "simulations.paired_effect_analysis", "DERIVED_STATISTICAL_COMPARISON"),
]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="validate experiment registry and write a manifest without running simulations")
    parser.add_argument("--smoke", action="store_true", help="run reduced configurations for experiments that explicitly support smoke mode")
    args = parser.parse_args(argv)

    out = Path("results/reproducibility")
    out.mkdir(parents=True, exist_ok=True)
    records: list[dict[str, object]] = []
    failed = False
    for experiment in EXPERIMENTS:
        command = experiment.command(smoke=args.smoke)
        if args.dry_run:
            records.append({"name": experiment.name, "command": " ".join(command), "classification": experiment.classification, "returncode": 0, "status": "registered"})
            print(f"[REGISTERED] {experiment.name}")
            continue
        proc = subprocess.run(command, text=True, capture_output=True)
        record = {"name": experiment.name, "command": " ".join(command), "classification": experiment.classification, "returncode": proc.returncode, "status": "success" if proc.returncode == 0 else "failed"}
        records.append(record)
        if proc.returncode != 0:
            failed = True
            print(f"[FAIL] {experiment.name}\n{proc.stdout}\n{proc.stderr}", file=sys.stderr)
        else:
            print(f"[OK] {experiment.name}")

    with (out / "experiment_status.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["name", "command", "classification", "returncode", "status"])
        writer.writeheader()
        writer.writerows(records)
    write_manifest(out / "run_manifest.json", records)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
