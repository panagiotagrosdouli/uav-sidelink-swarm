# Parameter provenance

This project distinguishes **MEASURED**, **STANDARD**, **LITERATURE**, **DERIVED**, **EXPERIMENTAL_SWEEP**, **EXPERIMENTAL_ASSUMPTION**, and **SYNTHETIC** quantities. A value must not be described as a real measurement unless it was obtained directly from a published measurement campaign or measured dataset.

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
| Measurement interval | 100 | ms | MEASURED campaign procedure | Sec. III-A/III-B | Records saved periodically |
| PN length | 4095 | samples | MEASURED campaign waveform | Sec. III-A / Table I | Channel sounding sequence |
| Delay resolution | 20 | ns | MEASURED campaign waveform | Table I | Channel sounder configuration |
| Maximum delay | 160 | us | MEASURED campaign waveform | Table I | Channel sounder configuration |
| A2A path-loss exponent, eta | 2.166 | - | DERIVED from measurements | Table II / Eq. (3) fit | Fitted large-scale A2A path-loss parameter |
| A2A PL0 | 34.650 | dB | DERIVED from measurements | Table II / Eq. (3) fit | Fitted intercept reported for A2A |
| Reference distance d0 | 1 | m | LITERATURE model definition | Eq. (3) | Reference distance used in model |

The large-scale A2A fit reproduced in this repository is:

`PL(d) = 34.650 + 10 * 2.166 * log10(d / 1 m)`

Important: values obtained by evaluating this fit at new distances are **DERIVED_FROM_MEASUREMENT_FIT**, not raw measured samples.

## 3GPP Release-19 aerial-to-aerial channel provenance

Primary standards source: **3GPP TR 38.901 V19.4.0 (Release 19), Clause 7.9.3, Case 9**. For an aerial-UE-to-aerial-UE link in UMi-AV/UMa-AV/RMa-AV, Case 9 reuses the TRP-aerial-UE channel from **3GPP TR 36.777 Annexes A/B**, setting the TRP height equal to the height of the first aerial UE.

The current implementation intentionally supports only an auditable equal-height UMi-AV subset.

| Parameter/model item | Value / rule | Type | Source location | Notes |
|---|---|---|---|---|
| A2A model selection | Case 9 aerial UE - aerial UE | STANDARD | TR 38.901 V19.4.0 Table 7.9.3-1 | UMi-AV/UMa-AV/RMa-AV |
| A2A model reuse | TRP-aerial UMi-AV with TRP height = first aerial UE height | STANDARD | TR 38.901 V19.4.0 Case 9 | FR1 basis, reused for FR2 as specified |
| Equal-height LOS probability, 22.5 < h <= 100 m | UMa-AV Table B-1 probability | STANDARD | TR 38.901 Table 7.9.3-5 -> TR 36.777 Table B-1 | Used only for equal-height helper |
| Equal-height LOS probability, 100 < h <= 300 m | 1.0 | STANDARD | TR 38.901 Table 7.9.3-5 | Case-9 rule |
| UMi-AV LOS path loss, 22.5 < h <= 300 m | `max(FSPL, 30.9 + (22.25 - 0.5 log10(h))*log10(d3D) + 20 log10(fc))` | STANDARD | TR 36.777 Table B-2 | fc in GHz, d in m, d2D <= 4 km |
| UMi-AV NLOS path loss, 22.5 < h <= 300 m | `max(PL_LOS, 32.4 + (43.2 - 7.6 log10(h))*log10(d3D) + 20 log10(fc))` | STANDARD | TR 36.777 Table B-2 | d2D <= 4 km |
| UMi-AV LOS shadow-fading std | `max(5 exp(-0.01 h), 2)` dB | STANDARD | TR 36.777 Table B-3 | 22.5 < h <= 300 m |
| UMi-AV NLOS shadow-fading std | 8 dB | STANDARD | TR 36.777 Table B-3 | 22.5 < h <= 300 m |

The implementation is a **large-scale model only**. It does not yet implement the Annex-B fast-fading channel impulse response.

## Density-study provenance

| Quantity | Value | Type | Rationale |
|---|---:|---|---|
| Swarm size | 5, 10, 20, 30, 50 UAVs | EXPERIMENTAL_SWEEP | Scalability study |
| Monte-Carlo seeds | 100 per swarm size | EXPERIMENTAL_SWEEP | Statistical stability |
| Area | 1000 x 1000 m | SYNTHETIC | Controlled geometry; not a measured flight area |
| Altitude | 100 m | MEASURED campaign value reused as scenario anchor | Same altitude as Erdemir A2A campaign |
| Carrier | 3.5 GHz | MEASURED campaign configuration | Erdemir et al. |
| Bandwidth | 50 MHz | MEASURED campaign configuration | Erdemir et al. |
| TX power | 30 dBm | MEASURED campaign configuration | Erdemir et al. |
| Link topology | disjoint Tx->Rx pairs | SYNTHETIC | Half-duplex-compatible pairs `(0->1),(2->3),...`; avoids artificial self-interference |
| Activity probability | 1.0 | EXPERIMENTAL_ASSUMPTION | Same-resource worst-case interference stress test |
| Receiver noise figure | 7 dB | EXPERIMENTAL_ASSUMPTION | Not reported by Erdemir et al.; must be sensitivity-tested |
| SINR threshold | 5 dB | EXPERIMENTAL_ASSUMPTION | Preliminary link-success proxy, not NR BLER |

## Values intentionally NOT called measured

The following are not measurements from the Erdemir et al. campaign:

- swarm size and Monte-Carlo seeds;
- random UAV placement;
- disjoint-pair topology and simultaneous resource reuse;
- receiver noise figure;
- SINR decoding threshold;
- scheduler/resource-pool configuration;
- packet delivery ratio inferred from a threshold;
- Shannon `B log2(1+SINR)` values.

These must remain labelled as experimental, synthetic, or derived quantities.

## Source verification status

- Peer-reviewed Erdemir DOI: **VERIFIED**.
- Erdemir measurement geometry/configuration: **VERIFIED against the open manuscript**.
- Erdemir A2A fitted `eta=2.166` and `PL0=34.650 dB`: **VERIFIED**.
- 3GPP TR 38.901 current cited version: **V19.4.0 Release 19, July 2026**.
- 3GPP aerial-to-aerial Case 9 model selection: **VERIFIED from Clause 7.9.3 / Tables 7.9.3-1 and 7.9.3-5**.
- TR 36.777 UMi-AV LOS/NLOS and shadow-fading equations: **IMPLEMENTED as an explicitly limited subset**.
- Exact raw Erdemir IQ/flight-log samples: **NOT present in this repository**.
- Full 3GPP fast fading: **NOT IMPLEMENTED**.
- Bit-accurate NR sidelink PHY/MAC/BLER: **NOT IMPLEMENTED**.
