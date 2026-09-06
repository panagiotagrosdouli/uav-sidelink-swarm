"""3GPP NR transport-block size helpers for PSSCH/PDSCH-like resource accounting.

Sources:
- 3GPP TS 38.214 V19.4.0, Clause 8.1.3.2 for PSSCH TBS determination,
  reusing the TBS procedure of Clause 5.1.3.2.

The resource-grid inputs (allocated PRBs, data symbols, DM-RS/other overhead) are
scenario/configuration inputs. The TBS quantization algorithm itself is STANDARD.
"""
from __future__ import annotations

import math

from src.sidelink.nr_mcs import get_mcs

# TS 38.214 Table 5.1.3.2-1, TBS values for N_info <= 3824.
SMALL_TBS_BITS = (
    24,32,40,48,56,64,72,80,88,96,104,112,120,128,136,144,152,160,168,176,
    184,192,208,224,240,256,272,288,304,320,336,352,368,384,408,432,456,480,
    504,528,552,576,608,640,672,704,736,768,808,848,888,928,984,1032,1064,
    1128,1160,1192,1224,1256,1288,1320,1352,1416,1480,1544,1608,1672,1736,
    1800,1864,1928,2024,2088,2152,2216,2280,2408,2472,2536,2600,2664,2728,
    2792,2856,2976,3104,3240,3368,3496,3624,3752,3824,
)


def data_re_per_prb(n_symbols: int, dmrs_re_per_prb: int = 0, other_overhead_re_per_prb: int = 0) -> int:
    """Return usable RE/PRB, capped by the 156-RE rule in TS 38.214.

    A PRB contains 12 subcarriers. DM-RS and other overhead are explicit inputs
    because their exact values depend on the configured sidelink resource pool.
    """
    if not 1 <= n_symbols <= 14:
        raise ValueError("n_symbols must be in 1..14")
    if dmrs_re_per_prb < 0 or other_overhead_re_per_prb < 0:
        raise ValueError("overhead RE counts must be non-negative")
    n_re_prime = 12 * n_symbols - dmrs_re_per_prb - other_overhead_re_per_prb
    return max(0, min(156, n_re_prime))


def n_info_bits(
    mcs_index: int,
    n_prb: int,
    n_symbols: int,
    layers: int = 1,
    dmrs_re_per_prb: int = 0,
    other_overhead_re_per_prb: int = 0,
    scaling: float = 1.0,
) -> float:
    if n_prb < 1 or layers < 1:
        raise ValueError("n_prb and layers must be >= 1")
    if not 0 < scaling <= 1:
        raise ValueError("scaling must be in (0,1]")
    mcs = get_mcs(mcs_index)
    n_re = data_re_per_prb(n_symbols, dmrs_re_per_prb, other_overhead_re_per_prb) * n_prb
    return n_re * mcs.modulation_order * mcs.target_code_rate * layers * scaling


def _round_half_up(x: float) -> int:
    return math.floor(x + 0.5)


def tbs_from_n_info(n_info: float, target_code_rate: float) -> int:
    """TS 38.214 TBS quantization, returning transport-block size in bits."""
    if n_info <= 0:
        raise ValueError("n_info must be positive")
    if not 0 < target_code_rate <= 1:
        raise ValueError("target_code_rate must be in (0,1]")

    if n_info <= 3824:
        n = max(3, math.floor(math.log2(n_info)) - 6)
        n_info_prime = max(24, (2**n) * math.floor(n_info / (2**n)))
        return next(v for v in SMALL_TBS_BITS if v >= n_info_prime)

    n = math.floor(math.log2(n_info - 24)) - 5
    step = 2**n
    n_info_prime = max(3840, step * _round_half_up((n_info - 24) / step))
    if target_code_rate <= 0.25:
        c = math.ceil((n_info_prime + 24) / 3816)
        return 8 * c * math.ceil((n_info_prime + 24) / (8 * c)) - 24
    if n_info_prime > 8424:
        c = math.ceil((n_info_prime + 24) / 8424)
        return 8 * c * math.ceil((n_info_prime + 24) / (8 * c)) - 24
    return 8 * math.ceil((n_info_prime + 24) / 8) - 24


def transport_block_size_bits(**kwargs) -> int:
    mcs = get_mcs(int(kwargs["mcs_index"]))
    return tbs_from_n_info(n_info_bits(**kwargs), mcs.target_code_rate)
