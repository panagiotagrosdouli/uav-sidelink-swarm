"""DEPRECATED entry point for the old density prototype.

The old sweep depended on ``src.sinr_sim`` and therefore inherited a conflicting
5.9 GHz baseline. Use ``simulations.density_measurement_based`` or the final
campaign instead.
"""
from __future__ import annotations

import warnings

from simulations.density_measurement_based import main as canonical_main


def main() -> None:
    warnings.warn(
        "simulations.run_density_sweep is deprecated; using density_measurement_based",
        DeprecationWarning,
        stacklevel=2,
    )
    canonical_main()


if __name__ == "__main__":
    main()
