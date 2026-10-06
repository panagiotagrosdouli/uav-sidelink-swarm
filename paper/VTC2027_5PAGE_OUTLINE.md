# VTC2027-Spring — topology-first 5-page compression outline

Target contribution: **measurement-grounded, NR-aware characterization of topology-conditioned UAV sidelink interference, exact resource-isolation trade-offs, and a joint reliability/goodput operating region.**

Current CFP deadline checked 2026-10-06: **14 October 2026 (final extension)**.

## Page budget

### Page 1 — Abstract + Introduction

The first page must establish four ideas quickly:

1. UAV sidelink scalability is not a function of swarm size alone.
2. Desired-link topology can fundamentally change the interference regime.
3. Resource isolation reduces interference but also removes PRBs/TBS from each link.
4. Spatial selectivity can complement frequency isolation.

State the research gap conservatively: existing work covers sidelink scheduling, analytical U2U outage, joint trajectory/frequency/routing optimization, topology control, and synchronization, but the joint NR-aware characterization of topology sensitivity + explicit resource-bandwidth cost + reliability/goodput operating region remains insufficiently characterized.

End with exactly three contributions:

1. measurement-grounded / NR-aware system evaluation;
2. topology-conditioned interference scaling with matched-seed nearest-neighbour sensitivity;
3. exact resource + spatial-selectivity operating envelope with allocator/fixed-MCS/bandwidth robustness controls.

### Page 2 — Related Work + System Model

Use one compact closest-work table including Mishra, Lau, Varonen, Alam and Moh, and Bai et al. Avoid claiming that topology control itself is novel.

System-model essentials only:

- 3.5 GHz measurement-derived A2A large-scale fit;
- 50 MHz / 30 kHz / 133 PRBs;
- standards-based MCS/TBS/LDPC mechanics;
- official 5G-LENA v5.0 Table-1 link-level BLER curves;
- exact PRB partitions R={1,2,4,8};
- G={0,3,6,9} dB experimental directional relative advantage;
- N={5,10,20,30,50,75,100};
- 100 matched deterministic seeds;
- full-load sequential-disjoint baseline plus nearest-neighbour robustness.

### Page 3 — Baseline + topology sensitivity

Show the baseline density trend but immediately condition it on topology.

Headline baseline at N=100,R=1,G=0:

- mean desired distance 517.20 m;
- mean SINR -23.03 dB;
- first-TX success 0.0128;
- expected goodput 0.359 Mbps.

Nearest-neighbour at the same N,R,G:

- mean desired distance 84.05 m;
- mean SINR -1.75 dB;
- first-TX success 0.4766;
- expected goodput 15.116 Mbps.

Primary interpretation: **density-only statements are not topology invariant**.

### Page 4 — Resource trade-off + joint operating envelope

At N=100,G=0 show:

| R | SINR dB | Success | Goodput Mbps |
|---:|---:|---:|---:|
| 1 | -23.03 | 0.0128 | 0.359 |
| 2 | -16.20 | 0.0749 | 0.668 |
| 4 | -10.48 | 0.0775 | 0.572 |
| 8 | -5.47 | 0.2049 | 1.042 |

Use R=2 -> R=4 as the key evidence that orthogonalization is not free.

Then show the compact operating envelope and one selected matched-seed comparison:

- N=100, R=8,G=6 vs R=1,G=0;
- success difference +0.516358, 95% CI [0.505829,0.526887];
- goodput difference +1.870079 Mbps, 95% CI [1.728555,2.011603].

### Page 5 — Discussion + Limitations + Conclusion + References

Discussion order:

1. topology is a first-order interference-management variable;
2. resource partitioning has a real bandwidth/TBS cost;
3. resource isolation and spatial selectivity are complementary;
4. retransmission cannot substitute for fixing a fundamentally poor SINR regime.

Limitations must remain adjacent to the claims:

- no measured multi-UAV RF/PDR/BLER/latency;
- no normative Mode-1/Mode-2 scheduler;
- no full MIMO/beam management or fast fading;
- idealized adaptive-MCS semantics;
- engineering-policy envelope thresholds;
- evaluated grid capped at N=100.

## Figure cap

Prefer exactly 3 main figures:

1. topology-conditioned density/interference figure;
2. exact resource-partition trade-off;
3. reliability/goodput operating-envelope heatmap.

A fourth figure should be added only if the IEEE layout remains readable.

## Excluded material

Keep routing, AMOVFLY mobility, traffic queues, ULA study, full HARQ sweep, thesis-wide ablation, and channel-model comparison in the reproducibility package rather than the 5-page core paper.