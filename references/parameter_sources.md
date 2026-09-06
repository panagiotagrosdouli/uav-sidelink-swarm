# Parameter provenance

This project distinguishes **MEASURED**, **STANDARD**, **LITERATURE**, **DERIVED**, **EXPERIMENTAL_SWEEP**, and **SYNTHETIC** quantities. A value must not be described as a real measurement unless it was obtained directly from a published measurement campaign or measured dataset.

## Measurement-based A2A baseline at 3.5 GHz

Primary peer-reviewed source:

U. Erdemir, B. Kaplan, I. Hokelek, A. Gorcin, H. A. Cirpan, *Measurement-based Channel Characterization for A2A and A2G Wireless Drone Communication Systems*, 2023 IEEE 97th Vehicular Technology Conference (VTC2023-Spring), DOI: **10.1109/VTC2023-Spring57618.2023.10199853**.

Open manuscript: arXiv:2306.08474.

| Parameter | Value | Unit | Type | Source location | Notes |
|---|---:|---|---|---|---|
| Center frequency | 3.5 | GHz | MEASURED campaign configuration | Sec. III-A / Table I | Channel sounder configuration |
| Bandwidth | 50 | MHz | MEASURED campaign configuration | Sec. III-A / Table I | Channel sounder configuration |
| Transmitted power | 30 | dBm | MEASURED campaign configuration | Sec. III-A / Table I | RF signal amplified to 30 dBm before antenna |
| UAV platform | DJI Matrice 600 Pro | - | MEASURED campaign hardware | Sec. III-B | Two drones used |
| TX altitude | 100 | m | MEASURED campaign geometry | Sec. III-B | A2A scenario |
| RX altitude | 100 | m | MEASURED campaign geometry | Sec. III-B | A2A scenario |
| Initial A2A distance | 85 | m | MEASURED campaign geometry | Sec. III-B | Initial TX/RX separation |
| TX flight speed | 3 | m/s | MEASURED campaign geometry | Sec. III-B | Constant speed |
| TX trajectory | 1000 | m | MEASURED campaign geometry | Sec. III-B | Straight trajectory |
| Measurement interval | 100 | ms | MEASURED campaign procedure | Sec. III-A/III-B | Samples/records saved periodically |
| PN length | 4095 | samples | MEASURED campaign waveform | Sec. III-A / Table I | Channel sounding sequence |
| A2A path-loss exponent, eta | 2.166 | - | DERIVED from measurements | Table II / measurement results | Fitted large-scale A2A path-loss parameter |
| A2A PL0 | 34.650 | dB | DERIVED from measurements | Table II / measurement results | Fitted intercept reported for A2A |
| Reference distance d0 | 1 | m | LITERATURE model definition | Eq. (3) / implementation convention | Used by the reproduced log-distance model |

The large-scale A2A fit reproduced in this repository is:

`PL(d) = 34.650 + 10 * 2.166 * log10(d / 1 m)`

Important: the fit is **measurement-derived**, but values produced by evaluating this equation at new distances are **DERIVED simulation/model outputs**, not raw measured samples.

## Values intentionally NOT called measured

The following are not measurements from the Erdemir et al. campaign:

- swarm size (e.g. 5, 10, 20, 30, 50 UAVs) — `EXPERIMENTAL_SWEEP`;
- random UAV placement — `SYNTHETIC`;
- traffic activity probability — `EXPERIMENTAL_SWEEP` or `SYNTHETIC`, depending on use;
- receiver noise figure unless traced to exact hardware — currently an assumption;
- arbitrary SINR decoding threshold — currently an assumption/proxy;
- scheduler/resource-pool configuration — must come from 3GPP or be labelled experimental;
- many-UAV interferer placement — synthetic unless a measured swarm dataset is used;
- packet delivery ratio from an SINR threshold — simulation proxy, never measured PDR;
- Shannon `B log2(1+SINR)` — theoretical upper bound, not NR throughput.

## Source verification status

- Peer-reviewed DOI: VERIFIED.
- Measurement geometry/configuration above: VERIFIED against the open manuscript.
- A2A fitted `eta=2.166` and `PL0=34.650 dB`: VERIFIED from Table II / reported fit results.
- Exact raw measurement samples: NOT present in this repository.
- Full 3GPP aerial channel implementation: NOT YET IMPLEMENTED.
