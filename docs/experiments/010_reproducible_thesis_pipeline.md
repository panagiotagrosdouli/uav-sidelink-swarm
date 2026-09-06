# Experiment 010 — Reproducible thesis pipeline

## Objective

Provide one auditable entry point that runs the implemented thesis experiment suite and records the exact software/runtime context used to produce the outputs.

## Command

```bash
python -m tools.run_thesis_pipeline
```

A lightweight registry/manifest validation without executing the simulations is available with:

```bash
python -m tools.run_thesis_pipeline --dry-run
```

## Outputs

- `results/reproducibility/experiment_status.csv`
- `results/reproducibility/run_manifest.json`

The manifest records the Git commit SHA, Python version, platform, selected package versions, the scientific provenance policy and the experiment registry.

## Registered experiments

1. Measurement-derived A2A propagation baseline.
2. FSPL vs measurement-derived vs 3GPP aerial large-scale channel comparison.
3. Density Monte Carlo study.
4. Resource-allocation abstraction study.
5. Routing study.
6. Beamforming sensitivity.
7. NR MCS + sourced BLER link-performance study.
8. TBS/LDPC/HARQ latency study.
9. Sidelink resource-overhead sensitivity.

## Provenance rule

The runner does not change the provenance of any quantity. `MEASURED`, `STANDARD`, `LINK_LEVEL_SIMULATION`, `DERIVED`, `EXPERIMENTAL_*` and `SYNTHETIC` classifications remain defined by the underlying experiment/source documentation.

## Boundary

The pipeline is a reproducibility/orchestration layer. It does not make the simulator bit-accurate and does not convert experimental assumptions into measurements.
