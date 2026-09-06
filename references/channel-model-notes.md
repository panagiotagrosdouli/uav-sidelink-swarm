# Channel-model notes

## Current implementation

`src/sinr_sim.py` currently uses free-space path loss (FSPL) only as a transparent LOS sanity-check baseline. It is **not** claimed to be a complete 3GPP NR Sidelink PHY or a complete 3GPP aerial channel implementation.

The simulator adds co-channel interference in linear power units and computes

`SINR = S / (N + sum(I_k))`.

The `success` field is a threshold-based PDR proxy, not a BLER curve from a specific NR MCS. The `shannon_upper_bound_mbps` field is a theoretical Shannon upper bound, not expected NR user throughput.

## Standards provenance

3GPP TR 38.901, *Study on channel model for frequencies from 0.5 to 100 GHz*, is maintained by RAN1. Release 19 introduced/clarified aerial-UE-related definitions and references for UMi/UMi-AV, UMa/UMa-AV and RMa/RMa-AV scenarios. Use the exact version cited by each thesis experiment because the document remains under change control.

Useful source:
- 3GPP specification 38.901 portal: https://portal.3gpp.org/desktopmodules/Specifications/SpecificationDetails.aspx?specificationId=3173
- ETSI publication of TR 138 901 V19.3.0 (2026-04): https://www.etsi.org/deliver/etsi_tr/138900_138999/138901/19.03.00_60/tr_138901v190300p.pdf

## Next implementation step

Before presenting results as a 3GPP aerial-channel experiment, implement and unit-test a selected scenario (UMi-AV, UMa-AV or RMa-AV) directly from the applicable clauses/tables of the chosen TR 38.901 version. Record:

- exact specification version;
- scenario and LOS/NLOS assumptions;
- carrier frequency and applicability range;
- 2D/3D distance definitions;
- UAV heights;
- shadow-fading distribution and standard deviation;
- any model limitations for aerial-to-aerial communication.

This separation is intentional: it prevents a simple FSPL simulation from being mislabeled as a standards-compliant 3GPP result.
