"""3GPP NR LDPC base-graph selection and code-block segmentation helpers.

Source: 3GPP TS 38.212 V19.4.0, Clauses 7.2.2 and 5.2.2.
These are STANDARD coding rules. This module does not implement LDPC encoding.
"""
from __future__ import annotations

import math


def select_base_graph(payload_bits: int, target_code_rate: float) -> int:
    """Return LDPC base graph 1 or 2 using TS 38.212 criteria."""
    if payload_bits <= 0:
        raise ValueError("payload_bits must be positive")
    if not 0 < target_code_rate <= 1:
        raise ValueError("target_code_rate must be in (0,1]")
    if payload_bits <= 292 or (payload_bits <= 3824 and target_code_rate <= 0.67) or target_code_rate <= 0.25:
        return 2
    return 1


def transport_block_crc_bits(payload_bits: int) -> int:
    """TB CRC length used by DL-SCH/UL-SCH style transport blocks.

    24 bits are used for payloads above 3824 bits, otherwise 16 bits.
    """
    if payload_bits <= 0:
        raise ValueError("payload_bits must be positive")
    return 24 if payload_bits > 3824 else 16


def code_block_segmentation(payload_bits: int, target_code_rate: float) -> dict[str, int]:
    """Return base graph, TB+CRC size, code-block count and nominal bits/block.

    The code-block count follows TS 38.212 Clause 5.2.2 with Kcb=8448 for BG1
    and Kcb=3840 for BG2. A 24-bit CRC is added to each code block only when
    segmentation is required.
    """
    bg = select_base_graph(payload_bits, target_code_rate)
    b = payload_bits + transport_block_crc_bits(payload_bits)
    kcb = 8448 if bg == 1 else 3840
    if b <= kcb:
        c = 1
        cb_crc = 0
        b_prime = b
    else:
        cb_crc = 24
        c = math.ceil(b / (kcb - cb_crc))
        b_prime = b + c * cb_crc
    nominal = math.ceil(b_prime / c)
    return {
        "base_graph": bg,
        "tb_plus_crc_bits": b,
        "code_blocks": c,
        "code_block_crc_bits": cb_crc,
        "segmented_bits": b_prime,
        "nominal_code_block_size": nominal,
    }
