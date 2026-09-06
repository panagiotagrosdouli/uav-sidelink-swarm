"""Explicit NR sidelink resource-grid accounting.

The module separates STANDARD mechanics from CONFIGURATION choices. 3GPP TS
38.211/38.214 define how PSSCH/PSCCH/DM-RS resources are mapped and how PSSCH
TBS is determined, but there is no single universal overhead percentage for all
resource pools. Therefore a concrete profile must state its PSCCH/PSSCH symbol
allocation and DM-RS RE count explicitly.

Current thesis profile is deliberately a CONFIGURED STUDY PROFILE, not a claim
that every NR sidelink deployment uses these values.
"""
from __future__ import annotations

from dataclasses import dataclass

from src.sidelink.nr_tbs import data_re_per_prb, transport_block_size_bits


@dataclass(frozen=True)
class SidelinkResourceGrid:
    """One explicit PSSCH allocation profile.

    n_pssch_symbols includes symbols occupied by PSSCH-associated DM-RS.
    dmrs_re_per_prb is the total DM-RS RE removed from one allocated PRB across
    those symbols. PSCCH is represented separately as symbols unavailable to
    PSSCH in this simplified contiguous-symbol study profile.
    """

    n_prb: int = 133
    n_slot_symbols: int = 14
    n_pscch_symbols: int = 2
    n_guard_symbols: int = 1
    n_pssch_symbols: int = 11
    dmrs_re_per_prb: int = 24
    other_overhead_re_per_prb: int = 0
    scs_khz: int = 30

    def __post_init__(self) -> None:
        if self.n_prb < 1:
            raise ValueError("n_prb must be positive")
        if self.n_pscch_symbols < 0 or self.n_guard_symbols < 0:
            raise ValueError("symbol overhead must be non-negative")
        if self.n_pssch_symbols < 1:
            raise ValueError("n_pssch_symbols must be positive")
        if self.n_pscch_symbols + self.n_guard_symbols + self.n_pssch_symbols > self.n_slot_symbols:
            raise ValueError("configured symbols exceed slot")

    @property
    def slot_duration_ms(self) -> float:
        # Normal-CP NR numerology: slot duration = 1 / 2^mu ms; 30 kHz => mu=1.
        if self.scs_khz != 30:
            raise ValueError("this thesis profile currently validates only 30 kHz SCS")
        return 0.5

    @property
    def usable_re_per_prb(self) -> int:
        return data_re_per_prb(
            n_symbols=self.n_pssch_symbols,
            dmrs_re_per_prb=self.dmrs_re_per_prb,
            other_overhead_re_per_prb=self.other_overhead_re_per_prb,
        )

    @property
    def raw_pssch_re_per_prb(self) -> int:
        return 12 * self.n_pssch_symbols

    @property
    def pssch_dmrs_overhead_fraction(self) -> float:
        return 1.0 - self.usable_re_per_prb / self.raw_pssch_re_per_prb

    def tbs_bits(self, mcs_index: int, layers: int = 1) -> int:
        return transport_block_size_bits(
            mcs_index=mcs_index,
            n_prb=self.n_prb,
            n_symbols=self.n_pssch_symbols,
            layers=layers,
            dmrs_re_per_prb=self.dmrs_re_per_prb,
            other_overhead_re_per_prb=self.other_overhead_re_per_prb,
        )


def thesis_profile_50mhz_30khz() -> SidelinkResourceGrid:
    """Concrete reproducible study profile for overhead sensitivity.

    STANDARD: 50 MHz / 30 kHz uses 133 PRBs; 30 kHz normal-CP slot is 0.5 ms.
    CONFIGURATION: 2 PSCCH symbols, 1 guard symbol, 11 PSSCH symbols and
    24 DM-RS RE/PRB are explicit thesis-study choices and MUST be sensitivity-
    tested rather than presented as universal 3GPP values.
    """
    return SidelinkResourceGrid()
