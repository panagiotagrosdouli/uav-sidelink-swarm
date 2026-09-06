# Parameter provenance

This project distinguishes **measured published values**, **standards-based values**, and **synthetic experiment variables**. A value must not be described as a real measurement unless it was obtained from a published measurement campaign or a dataset containing measured samples.

## Measurement-based A2A baseline at 3.5 GHz

Primary source: U. Erdemir, B. Kaplan, I. Hokelek, A. Gorcin, H. A. Cirpan, *Measurement-based Channel Characterization for A2A and A2G Wireless Drone Communication Systems*, 2023, arXiv:2306.08474.

| Parameter | Value | Classification | Source location |
|---|---:|---|---|
| Center frequency | 3.5 GHz | Measured campaign configuration | Measurement System / Table I |
| Bandwidth | 50 MHz | Measured campaign configuration | Measurement System / Table I |
| Transmitted power | 30 dBm | Measured campaign configuration | Measurement System / Table I |
| UAV platform | DJI Matrice 600 Pro | Measured campaign hardware | Measurement Environment |
| TX altitude | 100 m | Measured campaign geometry | Measurement Environment |
| RX altitude | 100 m | Measured campaign geometry | Measurement Environment |
| Initial A2A distance | 85 m | Measured campaign geometry | Measurement Environment |
| TX flight speed | 3 m/s | Measured campaign geometry | Measurement Environment |
| TX trajectory | 1 km straight route | Measured campaign geometry | Measurement Environment |
| Measurement interval | 100 ms | Measured campaign procedure | Measurement Environment |
| PN length | 4095 | Measured campaign waveform | Table I |
| Delay resolution | 20 ns | Measured campaign waveform | Table I |
| Maximum delay | 160 us | Measured campaign waveform | Table I |
| A2A path-loss exponent n | 2.166 | Measurement-derived fit | Measurement Results |
| A2A PL0 | 34.650 dB | Measurement-derived fit | Measurement Results |
| Reference distance | 1 m | Measurement-model definition | Measurement Results |

The A2A path-loss model used for the reproduction is:

`PL(d) = 34.650 + 10 * 2.166 * log10(d / 1 m)`

## Values intentionally NOT called measured

The following are not available as measured values from the cited A2A campaign and must remain clearly labelled if used later:

- swarm size (e.g. 5, 10, 20, 50 UAVs)
- traffic activity probability
- receiver noise figure unless sourced from the exact receiver hardware
- arbitrary SINR decoding threshold
- scheduler/resource-pool configuration
- interferer placement in a many-UAV swarm
- packet delivery ratio unless derived from a PHY/MAC model or measured packets

These quantities may be introduced later as experimental variables, standards-based parameters, or values from additional published measurements, but not as measurements from the Erdemir et al. campaign.
