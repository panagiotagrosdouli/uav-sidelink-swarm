# TBS / LDPC / HARQ parameter provenance

| Quantity | Value / rule | Classification | Source |
|---|---|---|---|
| MCS Table 1 | indices 0..28, Qm, R, spectral efficiency | STANDARD | 3GPP TS 38.214 V19.4.0 |
| PSSCH TBS procedure | Clause 8.1.3.2 reusing NR TBS determination | STANDARD | 3GPP TS 38.214 V19.4.0 |
| LDPC base graph | BG2 if A<=292, or A<=3824 and R<=0.67, or R<=0.25; otherwise BG1 | STANDARD | 3GPP TS 38.212 V19.4.0 |
| Maximum LDPC code block | BG1 8448 bits; BG2 3840 bits | STANDARD | 3GPP TS 38.212 V19.4.0 Clause 5.2.2 |
| Code-block CRC when segmented | 24 bits | STANDARD | 3GPP TS 38.212 V19.4.0 Clause 5.2.2 |
| FR1 profile | 50 MHz, 30 kHz SCS, 133 PRBs | STANDARD-CONFIGURATION | 3GPP TS 38.104 Table 5.3.2-1 |
| Numerology | mu=1, 0.5 ms slot | STANDARD-DERIVED | 3GPP TS 38.211 |
| SINR->BLER curves | 5G-LENA EESM numerical tables | LINK_LEVEL_SIMULATION | 5G-LENA v5.0 / nr-eesm-t1.cc |
| TB BLER from multiple CBs | `1-(1-CB_BLER)^C` | DERIVED / SYSTEM_LEVEL_APPROXIMATION | This work |
| Chase combining | sum linear SINR across repeated observations | DERIVED / IDEALIZED_CC | This work; compatible with ideal CC concept, not full 5G-LENA history processing |
| Maximum HARQ attempts | 4 in Experiment 008 | EXPERIMENTAL_PROFILE | This work |
| Feedback/re-tx gap | 1,2,4,8 slots sweep | EXPERIMENTAL_SWEEP | This work; exact timing is resource-pool/scheduler dependent |
| PSSCH DM-RS/PSCCH overhead in Experiment 008 | zero overhead | IDEALIZED_UPPER_BOUND | This work; MUST be replaced before final throughput claim |

## Non-claims

The Python layer does not claim a bit-accurate LDPC encoder/decoder, exact 5G-LENA IR history processing, a universal PSFCH retransmission gap, or measured UAV-swarm HARQ latency. It combines standards-defined coding/TBS rules with published link-level BLER data and explicitly-labelled system-level abstractions.
