"""DEPRECATED legacy density sweep.

This historical script used `src.sinr_sim.Config` with a 5.9 GHz / 20 MHz FSPL
baseline and a ring-link abstraction. It is intentionally excluded from the
scientific thesis pipeline because the current canonical studies use
`src.swarm_system` with explicit provenance and the 3.5 GHz measurement-derived
baseline. Run `python -m simulations.density_measurement_based` or
`python -m simulations.scaling_geometry_activity_study` instead.
"""
from __future__ import annotations

import warnings


def main() -> None:
    warnings.warn(
        "simulations.run_density_sweep is deprecated; use density_measurement_based or scaling_geometry_activity_study",
        DeprecationWarning,
        stacklevel=2,
    )
    raise SystemExit(
        "Deprecated scientific baseline: this script used conflicting 5.9 GHz/20 MHz assumptions. "
        "Use `python -m simulations.density_measurement_based`."
    )


if __name__ == "__main__":
    main()
