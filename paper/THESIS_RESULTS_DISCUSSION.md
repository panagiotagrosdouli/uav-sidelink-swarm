# Thesis Results and Discussion Synthesis

This chapter is derived from the current canonical final-thesis campaign. All RF/network quantities below are simulation/model-derived unless explicitly identified as measured telemetry.

## 1. Experimental basis

The canonical campaign evaluates swarm sizes N = {5, 10, 20, 30, 50, 75, 100}, 1/2/4/8 abstract orthogonal frequency resources, and directional relative desired/interferer advantages G = {0, 3, 6, 9} dB. The main Monte-Carlo studies use 100 deterministic matched seeds. The final readiness audit records 18/18 successful registered experiments, 17/17 canonical figures, 304 scientific audit checks, and zero audit failures.

The evaluated communication model combines a 3.5 GHz measurement-derived large-scale A2A path-loss fit, standards-based NR MCS/TBS/LDPC mechanics, and numerical SINR-to-BLER curves processed from official 5G-LENA v5.0 link-level evidence. The resource allocator and directional model are explicit research abstractions and must not be interpreted as standards-complete NR sidelink scheduling or full MIMO beam management.

## 2. Density scaling

The principal baseline result is a strong density-dependent degradation under one shared frequency resource with no directional advantage. Mean SINR decreases from -0.49 dB at N=5 to -23.03 dB at N=100. At N=100, mean first-transmission success is 0.0128 and expected PHY goodput is 0.359 Mbps.

The failure diagnostic indicates that the dense regime is predominantly aggregate-interference limited. Approximately 72.4% of policy-failed links at N=100 are classified as aggregate-interference dominated, compared with 27.6% classified as dominant-interferer failures. This supports the interpretation that increasing swarm density changes the problem from isolated strong interferers toward many simultaneous co-channel contributors.

The scaling study therefore provides the first layer of the thesis argument: dense aerial sidelink cannot be characterized only by desired-link propagation quality. Because line-of-sight propagation benefits desired and interfering transmitters simultaneously, aggregate interference becomes the dominant system-level constraint as the number of active UAVs increases.

## 3. Frequency-resource separation

At N=100 and G=0 dB, exact PRB partitioning produces the following canonical means:

| Resources R | Mean SINR (dB) | First-TX success | Expected PHY goodput (Mbps) |
|---:|---:|---:|---:|
| 1 | -23.03 | 0.0128 | 0.359 |
| 2 | -16.20 | 0.0749 | 0.668 |
| 4 | -10.48 | 0.0775 | 0.572 |
| 8 | -5.47 | 0.2049 | 1.042 |

The result demonstrates a non-trivial bandwidth/interference trade-off. Increasing R reduces the number of co-channel interferers, but it also reduces the PRBs, occupied bandwidth and transport-block size available to an individual link. Consequently, more frequency resources do not guarantee monotonically increasing goodput. The R=2 to R=4 comparison is an explicit example: SINR improves, but expected goodput decreases because the bandwidth/TBS penalty outweighs the additional interference relief under that configuration.

The R=8 configuration is the first point in this G=0 sweep to satisfy both thesis policy targets at N=100: mean first-transmission success >= 0.10 and expected PHY goodput >= 1 Mbps.

## 4. Directionality

Directional relative advantage is modeled experimentally by applying +G/2 dB to the desired link and -G/2 dB to co-channel interference. At N=100 with R=1, increasing G from 0 to 9 dB changes mean SINR from -23.03 dB to -14.03 dB and expected goodput from 0.359 Mbps to 1.435 Mbps. However, first-transmission success remains only 0.0494 at G=9 dB and therefore does not satisfy the 0.10 reliability target.

This result is important because it separates throughput improvement from reliability feasibility. A directional mechanism can improve the desired/interference power balance substantially while still leaving the operating point in a high-BLER regime. Directionality is therefore most useful when combined with sufficient frequency isolation rather than treated as a complete substitute for resource coordination.

## 5. Cross-layer mitigation

At N=100, the principal mitigation configurations are:

| R | G (dB) | Mean SINR (dB) | First-TX success | Expected PHY goodput (Mbps) |
|---:|---:|---:|---:|---:|
| 1 | 0 | -23.03 | 0.0128 | 0.359 |
| 8 | 0 | -5.47 | 0.2049 | 1.042 |
| 2 | 6 | -10.20 | 0.1262 | 1.414 |
| 4 | 6 | -4.48 | 0.2193 | 1.608 |
| 8 | 6 | 0.53 | 0.5292 | 2.229 |
| 8 | 9 | 3.53 | 0.8050 | 3.493 |

The strongest combined case evaluated, R=8 and G=9 dB, reaches 0.805 first-transmission success and 3.493 Mbps expected PHY goodput at N=100. The R=8, G=6 dB configuration is a useful balanced point because it already reaches 0.529 success and 2.229 Mbps goodput without requiring the largest directional sweep value.

Relative to the R=1,G=0 baseline, R=8,G=6 improves mean SINR by 23.55 dB, first-transmission success by 0.516358, and expected PHY goodput by 1.870079 Mbps. Across 100 matched deterministic seeds, the first-transmission success difference has 95% CI [0.505829, 0.526887] and Cohen dz = 9.6122 (paired t-test p = 1.4474e-99). The goodput difference has 95% CI [1.728555, 2.011603] Mbps and Cohen dz = 2.5899 (paired t-test p = 6.9415e-46). These are paired system-level comparisons under identical deterministic seeds, not independent field trials.

## 6. Operating envelope

The thesis operating envelope is defined by two explicit engineering-policy targets:

- mean first-transmission success >= 0.10;
- mean expected PHY goodput >= 1 Mbps.

The resulting largest **evaluated** feasible swarm sizes are:

| Resources R | G=0 dB | G=3 dB | G=6 dB | G=9 dB |
|---:|---:|---:|---:|---:|
| 1 | 10 | 10 | 20 | 50 |
| 2 | 50 | 75 | 100 | 100 |
| 4 | 50 | 75 | 100 | 100 |
| 8 | 100 | 100 | 100 | 100 |

These values must be interpreted as boundaries of the evaluated grid, not universal UAV swarm capacity limits. In particular, because N=100 is the largest simulated swarm size, a value of 100 means that the target was still satisfied at the largest evaluated point; it does not prove feasibility for N>100.

## 7. HARQ, routing, mobility and auxiliary studies

The wider campaign includes TBS/LDPC/CBS/HARQ latency, routing, traffic-load, spatial diagnostics, synthetic mobility, AMOVFLY mobility evidence, fairness and cross-layer ablation studies. These experiments provide supporting context rather than changing the central density/resource/directionality conclusion.

HARQ is modeled as an idealized Chase-combining abstraction. It therefore should be discussed as a sensitivity/context mechanism rather than as an exact recreation of NR incremental-redundancy history. Likewise, routing is a graph/path abstraction and the AMOVFLY evidence establishes mobility/trajectory information; it does not constitute measured swarm RF interference, measured BLER/PDR or measured end-to-end latency.

## 8. Discussion

The results support a cross-layer interpretation of dense UAV sidelink. First, density changes the interference regime itself: as more transmitters share the same resource, aggregate interference dominates and the first transmission can enter a near-certain failure regime. Second, frequency separation is effective because it acts directly on the number of co-channel interferers, but its benefit is constrained by reduced per-link bandwidth and transport-block size. Third, directionality changes the desired-to-interference balance and becomes substantially more effective when combined with resource isolation.

This ordering has a practical design implication. Mitigation should act before retransmission: reducing interference at the resource and spatial levels can move the operating point into a region where the first transmission is already sufficiently reliable. Retransmission mechanisms can then provide additional robustness rather than compensate for an inherently interference-limited operating point.

The project therefore motivates future standards-compliant work on coordinated resource selection, adaptive resource reuse, and physical beam management for aerial sidelink. The present implementation deliberately stops at an auditable system-level abstraction so that the causal effect of density, resource partitioning and spatial selectivity can be isolated and reproduced.

## 9. Limitations and scientific boundary

The following limitations are part of the interpretation of the results:

1. Simulated RF/network quantities are model-derived. The A2A path-loss law is fitted from published measurements but is not a collection of raw swarm RF measurements.
2. The numerical BLER evidence is link-level simulation data from official 5G-LENA v5.0 processing, not a 3GPP-standard BLER table.
3. Resource allocation is a `THIS_WORK` conflict-graph abstraction, not normative NR Sidelink Mode 1/Mode 2 scheduling.
4. Directionality is an experimental relative desired/interferer sensitivity sweep, not full MIMO or beam management.
5. HARQ is an ideal Chase-combining abstraction rather than an exact incremental-redundancy implementation.
6. Full fast fading is outside the current model scope.
7. The operating-envelope thresholds are engineering-policy choices, not 3GPP requirements.
8. The reported envelope is limited to the evaluated N grid and must not be generalized into a universal swarm-capacity statement.

## 10. Thesis conclusion

The canonical evidence demonstrates that dense NR sidelink UAV swarms become strongly interference-limited when many transmitters share the same aerial resource. In the evaluated system model, mean SINR falls from -0.49 dB at N=5 to -23.03 dB at N=100 under the one-resource baseline, while first-transmission success falls to 0.0128 and expected PHY goodput to 0.359 Mbps. Exact frequency-resource separation substantially mitigates this degradation, but its benefit is constrained by the corresponding bandwidth and transport-block reduction. Directional spatial selectivity provides an additional interference-management dimension, with the strongest evaluated combined configuration reaching 0.805 first-transmission success and 3.493 Mbps expected PHY goodput at N=100.

The central conclusion is therefore not that a fixed number of UAVs is supported. Rather, the evidence shows that the feasible operating region is jointly controlled by swarm density, resource isolation and desired/interferer spatial selectivity. Within the evaluated model and explicit engineering-policy targets, cross-layer mitigation can shift the system from a severe interference-limited regime to a substantially more reliable operating region. This conclusion is reproducible within the documented scope and provides a quantitative basis for future standards-compliant and experimentally validated UAV sidelink research.