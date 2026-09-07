# VTC2027-Spring — 5-page compression outline

Target contribution: **measurement-grounded, NR-aware characterization of the interference operating envelope of dense UAV sidelink under exact frequency-resource partitioning and directional spatial selectivity.**

## Page budget

### Page 1 — Abstract + Introduction

Keep the abstract close to 150–180 words. Introduction should establish: (i) NR sidelink relevance to infrastructure-independent UAV swarm coordination; (ii) dense aerial LOS creates strong aggregate interference; (iii) resource isolation trades interference against PRB/TBS bandwidth; (iv) spatial selectivity can complement frequency isolation.

End the introduction with exactly three contributions:

1. measurement-grounded / NR-aware system evaluation;
2. density-dependent interference characterization;
3. exact-resource + directionality operating envelope.

Do not discuss routing, traffic, AMOVFLY, HARQ details, or thesis-wide experiments here.

### Page 2 — Related Work + System Model

Related work: compress to 4–6 closest references and one paragraph. Contrast against:

- 5G sidelink UAV swarm scheduling/network formation;
- analytical multi-UAV U2U outage/interference;
- NR sidelink UAV-swarm suitability/routing;
- joint trajectory/frequency/routing optimization;
- recent synchronization-oriented UAV sidelink work.

System model must preserve only the assumptions reviewers need to interpret the results:

- 3.5 GHz measurement-derived A2A large-scale fit;
- 50 MHz / 30 kHz / 133 PRBs;
- standards-based MCS/TBS/LDPC mechanics;
- official 5G-LENA v5.0 Table-1 link-level BLER curves;
- exact PRB partitions for R={1,2,4,8};
- G={0,3,6,9} dB experimental directional relative advantage;
- N={5,10,20,30,50,75,100}, 100 matched seeds.

Use one compact table for parameters/provenance.

### Page 3 — Baseline density + resource trade-off

Primary figure candidate: baseline density scaling and failure-regime composition, or a compact two-panel equivalent if the final template allows it.

Headline facts:

- mean SINR -0.49 dB at N=5 -> -23.03 dB at N=100;
- at N=100 baseline first-TX success 0.0128, expected goodput 0.359 Mbps;
- ~72.4% of policy-failed links aggregate-interference dominated at N=100.

Then show the exact-resource cost/benefit at N=100:

| R | SINR dB | Success | Goodput Mbps |
|---:|---:|---:|---:|
| 1 | -23.03 | 0.0128 | 0.359 |
| 2 | -16.20 | 0.0749 | 0.668 |
| 4 | -10.48 | 0.0775 | 0.572 |
| 8 | -5.47 | 0.2049 | 1.042 |

Emphasize R=2 -> R=4 non-monotonic goodput as evidence that orthogonalization is not free.

### Page 4 — Cross-layer operating envelope

Primary figure candidate: operating-envelope heatmap/table over R and G, plus one selected N=100 comparison.

Frozen envelope under success>=0.10 and expected goodput>=1 Mbps:

| R | G=0 | G=3 | G=6 | G=9 |
|---:|---:|---:|---:|---:|
| 1 | 10 | 10 | 20 | 50 |
| 2 | 50 | 75 | 100 | 100 |
| 4 | 50 | 75 | 100 | 100 |
| 8 | 100 | 100 | 100 | 100 |

At N=100, R=8,G=6 versus R=1,G=0:

- success difference +0.516358; 95% CI [0.505829,0.526887]; Cohen dz=9.6122; p=1.4474e-99;
- expected goodput difference +1.870079 Mbps; 95% CI [1.728555,2.011603]; dz=2.5899; p=6.9415e-46.

State explicitly that N=100 is the evaluated grid boundary, not a universal capacity limit.

### Page 5 — Discussion + Limitations + Conclusion + References

Discussion should make only three design points:

1. dense swarm failure is aggregate-interference driven;
2. exact resource separation trades SINR improvement against bandwidth/TBS loss;
3. frequency isolation and spatial selectivity are complementary and should act before retransmission.

Limitations in one compact paragraph:

- no measured multi-UAV RF/PDR/BLER/latency;
- no normative Mode-1/Mode-2 scheduler;
- no full MIMO/beam management or fast-fading validation;
- BLER curves are 5G-LENA link-level simulation evidence;
- envelope thresholds are engineering policy choices.

Conclusion: one paragraph, no new claims.

## Main-paper figure cap

Prefer 3 main figures, maximum 4:

1. density/failure-regime figure;
2. resource-partition trade-off figure or compact N=100 table;
3. operating-envelope heatmap;
4. optional matched-effect / selected cross-layer comparison if space permits.

## Material intentionally excluded from the 5-page paper

Routing, AMOVFLY mobility, traffic queues, ULA physical-array study, full HARQ sweep, full thesis ablation, channel-model comparison, robustness sweeps, and spatial diagnostics remain reproducibility/supporting evidence in the repository but are not needed to establish this paper's central claim.

## Frozen evidence anchor

All quantitative values above trace to canonical scientific commit `9fb112307270d9d39408e704f285ea91d20a735b`, workflow run #3, artifact ID `10005074790`, digest `sha256:4a996afe9dffa7984a5a0cfa6276a6f727228cd1ee2cbbd6e7f1634e8c149137`.