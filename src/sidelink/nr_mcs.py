"""3GPP NR MCS Table 1 values used by sidelink PSSCH.

Source: 3GPP TS 38.214 V19.4.0 (Release 19), Table 5.1.3.1-1.
Clause 8.1.3.1 reuses the selected NR MCS table for PSSCH to determine
modulation order Qm and target code rate R.

These are STANDARD values, not measurements.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class McsEntry:
    index: int
    modulation_order: int
    target_code_rate_x1024: int
    spectral_efficiency: float

    @property
    def target_code_rate(self) -> float:
        return self.target_code_rate_x1024 / 1024.0


_TABLE1_RAW = [
    (0, 2, 120, 0.2344), (1, 2, 157, 0.3066), (2, 2, 193, 0.3770),
    (3, 2, 251, 0.4902), (4, 2, 308, 0.6016), (5, 2, 379, 0.7402),
    (6, 2, 449, 0.8770), (7, 2, 526, 1.0273), (8, 2, 602, 1.1758),
    (9, 2, 679, 1.3262), (10, 4, 340, 1.3281), (11, 4, 378, 1.4766),
    (12, 4, 434, 1.6953), (13, 4, 490, 1.9141), (14, 4, 553, 2.1602),
    (15, 4, 616, 2.4063), (16, 4, 658, 2.5703), (17, 6, 438, 2.5664),
    (18, 6, 466, 2.7305), (19, 6, 517, 3.0293), (20, 6, 567, 3.3223),
    (21, 6, 616, 3.6094), (22, 6, 666, 3.9023), (23, 6, 719, 4.2129),
    (24, 6, 772, 4.5234), (25, 6, 822, 4.8164), (26, 6, 873, 5.1152),
    (27, 6, 910, 5.3320), (28, 6, 948, 5.5547),
]

MCS_TABLE_1 = tuple(McsEntry(*row) for row in _TABLE1_RAW)
_MCS_BY_INDEX = {entry.index: entry for entry in MCS_TABLE_1}


def get_mcs(index: int) -> McsEntry:
    """Return a valid, non-reserved Table-1 MCS entry (0..28)."""
    try:
        return _MCS_BY_INDEX[index]
    except KeyError as exc:
        raise ValueError("MCS Table 1 index must be in 0..28") from exc


def standards_spectral_efficiency(index: int) -> float:
    return get_mcs(index).spectral_efficiency
