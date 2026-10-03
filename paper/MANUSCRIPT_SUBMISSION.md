# Interference Scaling and Cross-Layer Mitigation in 5G NR Sidelink UAV Swarms

> **Submission draft.** All numerical RF/network results reported here are simulation/model-derived unless explicitly stated otherwise. The paper does not claim measured multi-UAV RF performance.

## Abstract

Direct NR sidelink is attractive for infrastructure-independent communication inside unmanned aerial vehicle (UAV) swarms, but dense line-of-sight aerial deployments can become strongly interference-limited. This paper characterizes how swarm density, exact frequency-resource partitioning, resource assignment, and directional spatial selectivity jointly determine an evaluated reliability/goodput operating region. The system model combines a published measurement-derived 3.5 GHz air-to-air large-scale path-loss fit, standards-based NR MCS/TBS/LDPC mechanics, and SINR-to-BLER curves processed from the official 5G-LENA v5.0 link-level dataset. A 100-seed campaign evaluates 5–100 UAVs and exact partitions of a 133-PRB, 50 MHz / 30 kHz profile into 1, 2, 4, or 8 resources; occupied noise bandwidth is computed from the allocated PRB subcarriers. Under the primary geometry-independent disjoint peer-pairing regime, mean SINR falls from -0.49 dB at 5 UAVs to -23.03 dB at 100 UAVs. At N=100, the R=1,G=0 baseline gives 0.0128 first-transmission success and 0.359 Mbps expected PHY goodput, whereas R=8,G=6 gives 0.5292 and 2.229 Mbps. The matched-seed differences are +0.5164 success (bootstrap 95% CI [0.5057, 0.5268], Cohen dz=9.61) and +1.870 Mbps goodput (bootstrap 95% CI [1.717, 2.003], dz=2.59). Matched random-allocation baselines show that both frequency partitioning and the conflict-graph assignment heuristic contribute to the gain. A nearest-neighbour pairing sensitivity further shows that traffic locality is a major boundary condition: at N=100, the shared-resource baseline rises to 0.477 success and 15.12 Mbps because the mean desired-link distance falls from 517 m to 84 m. The reported envelope is therefore conditional on an explicit communication-topology regime, not a universal UAV-swarm capacity limit.

## 1. Introduction

UAV swarms require frequent exchange of position, status, control, coordination, and mission information. Direct device-to-device communication is attractive because swarm operation may occur outside reliable infrastructure coverage and because local coordination traffic should not necessarily traverse a base station. NR sidelink provides a standardized direct-transmission framework and is therefore a natural candidate for intra-swarm communication.

Aerial propagation creates a difficult interference regime. Strong line-of-sight conditions benefit the desired link but can also strengthen many simultaneous interferers. As swarm density grows, a shared sidelink resource can transition from sparse interference to aggregate-interference domination. Retransmission does not remove this root cause when first-transmission BLER is already near one. Frequency orthogonalization can reduce the number of co-channel interferers, but it also reduces the PRBs and transport-block size available to each transmission. Directional transmission can further improve the desired-to-interference balance, although its value depends on the level of resource isolation already present.

This paper asks:

> **How does UAV swarm density change the interference regime of NR sidelink, and how far can frequency-resource separation and directional spatial selectivity extend the feasible reliability/goodput operating region?**

The paper makes three contributions. First, it provides a measurement-grounded, NR-aware system evaluation that combines a published 3.5 GHz A2A path-loss fit, standards-based NR transport-block mechanics, and sourced 5G-LENA v5.0 BLER curves. Second, it quantifies density-dependent degradation in SINR, first-transmission success, expected PHY goodput, fairness, and failure composition from 5 to 100 UAVs under a controlled geometry-independent peer-pairing regime designed to keep the desired-link distance distribution approximately invariant with swarm size. Third, it constructs an exact-resource operating envelope in which the 133-PRB profile is partitioned into 1/2/4/8 resources and per-resource occupied bandwidth, noise, TBS, LDPC/CBS, and BLER mappings are recomputed, while matched-seed random-allocation and nearest-neighbour-pairing sensitivities separate the effects of frequency isolation, assignment policy, and communication locality.

The study is intentionally system-level. It does not claim a bit-accurate NR sidelink PHY, normative Mode-1/Mode-2 scheduling, measured swarm PDR/BLER/latency, or full MIMO/beam-management behavior. In particular, the operating envelope is conditional on the explicitly stated pairing, traffic, allocation, and propagation assumptions.

## 2. Related Work

Mishra et al. studied cooperative C-U2X communication based on 5G sidelink for UAV swarms, emphasizing multi-hop communication and communication-aware channel scheduling [1]. Their work establishes the relevance of sidelink to UAV swarm networking, while the present study focuses on a density-resource-directionality operating envelope with NR TBS/LDPC-aware link evaluation.

Lau et al. derived a general analytical outage model for U2U links in multi-UAV networks and evaluated the effect of network parameters on SINR, outage probability, and capacity-related metrics [2]. Their analytical characterization is complementary to the present approach, which maps system SINR through sourced NR-oriented link-level BLER curves and exact transport-block/resource mechanics.

Varonen evaluated NR sidelink for UAV swarm internal communication and studied routing-update requirements [3]. The present work moves from suitability analysis toward quantitative dense-swarm operating-region characterization.

Recent UAV-swarm research has also emphasized joint optimization of trajectory, frequency allocation, and routing using multi-agent learning [4]. The goal here is different: resource assignment is deliberately kept as an auditable system-level abstraction so that density, bandwidth partitioning, and spatial selectivity can be isolated rather than hidden inside an optimizer.

Giannakoulas et al. reported sidelink communication for unmanned-platform swarms in challenging scenarios [5], while Zhang et al. recently addressed UAV-swarm sidelink synchronization and Doppler-related access/synchronization design [6]. These works reinforce that sidelink UAV swarms are an active research area, but they target different protocol and system questions.

The contribution of this paper is therefore not the generic use of sidelink in UAV swarms. It is a reproducible, measurement-grounded and NR-aware characterization of how density, exact resource isolation, and directional selectivity jointly shape the evaluated reliability/goodput operating region.

## 3. System Model and Scientific Provenance

### 3.1 Air-to-air propagation

The baseline large-scale A2A channel uses the fitted path-loss model reported by Erdemir et al. at 3.5 GHz [7]:

`PL(d) = 34.650 + 10 * 2.166 * log10(d / 1 m)`.

The coefficients are derived fitted parameters from a published measurement campaign, not raw samples. RF values produced at arbitrary simulated distances are therefore derived from a measurement-based model and must not be interpreted as field measurements.

### 3.2 NR resource profile, geometry, and transport-block mechanics

Table I lists the primary publication configuration. The nominal carrier profile is 3.5 GHz, 50 MHz channel bandwidth, 30 kHz subcarrier spacing, 133 PRBs, and 0.5 ms slots. Thermal-noise bandwidth is not taken as the nominal 50 MHz for every partition: for a resource containing n_PRB allocated PRBs, the occupied bandwidth is B_occ = n_PRB x 12 x 30 kHz. Hence the full 133-PRB allocation occupies 47.88 MHz of PRB subcarriers. NR MCS Table-1 parameters, TBS quantization, LDPC base-graph selection, and code-block segmentation follow the project implementation of Release-19 rules. The selected PSCCH/PSSCH/guard/DM-RS overhead profile is an explicit study configuration rather than a universal sidelink resource-pool requirement.

| Parameter | Primary value | Classification |
|---|---:|---|
| Carrier frequency | 3.5 GHz | study profile |
| Nominal channel / SCS | 50 MHz / 30 kHz | study profile |
| PRBs / slot duration | 133 / 0.5 ms | standards-based profile |
| Tx power | 30 dBm | experimental configuration |
| Receiver noise figure | 7 dB | experimental configuration |
| Deployment area | 1000 m x 1000 m | experimental configuration |
| UAV altitude | 100 m, equal height | experimental configuration |
| Activity probability | 1.0 | experimental configuration |
| Primary pairing | geometry-independent disjoint index pairs | THIS_WORK control regime |
| Primary R>1 allocator | weighted conflict graph | THIS_WORK |
| Monte Carlo seeds | 100 matched deterministic seeds | experiment design |

Because UAV positions are independently randomized for each seed while index pairs are fixed, the primary pairing is geometry-independent and its desired-link distance distribution remains approximately stable as N changes. This is useful for isolating density-driven interference growth, but it is not asserted to represent all swarm traffic patterns. Section 5.6 therefore repeats selected cases with nearest-neighbour disjoint pairing.

### 3.3 BLER evidence

For each candidate MCS, the computed TBS determines LDPC base graph and nominal code-block size. The request is mapped to the closest sourced 5G-LENA v5.0 curve for the same MCS/base graph, and transport-block BLER is derived from code-block BLER under an independent-code-block approximation.

The canonical publication run used the official CTTC 5G-LENA v5.0 Table-1 source: release short commit `47a3adc2`, DOI `10.5281/zenodo.21165297`, 1,332 sourced curves, BG1/BG2, and MCS 0–28. These numerical curves are **LINK_LEVEL_SIMULATION** evidence; they are neither UAV field measurements nor 3GPP-standard BLER tables.

### 3.4 Exact resource partitioning and assignment

The 133 PRBs are partitioned as evenly as possible:

- R=1: 133 PRBs (47.88 MHz occupied PRB bandwidth);
- R=2: 67+66 PRBs (24.12/23.76 MHz);
- R=4: 34+33+33+33 PRBs (12.24/11.88 MHz);
- R=8: 17+17+17+17+17+16+16+16 PRBs (6.12/5.76 MHz).

Links on different abstract frequency resources do not interfere in the system model. For every assigned resource, occupied noise bandwidth, TBS, LDPC segmentation, requested CBS, and sourced BLER mapping are recomputed. Resource separation is therefore not modeled as free interference removal while retaining the full 50 MHz payload resource.

The primary assignment uses a weighted conflict-graph heuristic developed in this project. Its pairwise geometric weight is proportional to the reciprocal-squared cross-link distances, and each link is greedily placed on the resource with the lowest accumulated conflict. It is **THIS_WORK**, not normative NR sidelink Mode-1/Mode-2 scheduling. To prevent the resource-partitioning result from being conflated with this heuristic, matched-seed random resource assignment is evaluated separately at N={10,50,100}, R={2,4,8}, and G={0,6} dB.

### 3.5 Directionality abstraction

The experimental directional relative advantage `G` in {0,3,6,9} dB is implemented as `+G/2` dB on the desired link and `-G/2` dB on co-channel interference. The relative desired/interferer advantage is therefore `G` dB. This is an **EXPERIMENTAL_SWEEP** sensitivity variable, not a measured antenna gain or full MIMO/beam-management model.

### 3.6 Monte Carlo and statistical design

The primary campaign evaluates N={5,10,20,30,50,75,100} UAVs. Each full (N,R,G) point uses 100 deterministic matched seeds and disjoint transmitter/receiver pairs. The primary grid contains 11,200 per-seed realizations and 112 scenario summaries.

Matched seeds are used whenever two mechanisms are compared so that the geometry realization is held fixed. For headline differences we report the paired mean difference, a Student-t 95% confidence interval, a deterministic 10,000-resample percentile-bootstrap 95% confidence interval, Cohen's dz, and a Wilcoxon signed-rank sensitivity check. Effect magnitudes and confidence intervals are treated as the primary evidence; p-values are secondary. These statistics describe repeated simulation realizations, not independent field trials.

Two reviewer-facing robustness families are evaluated with the same PHY/link path: (i) random versus weighted conflict-graph resource assignment and (ii) primary geometry-independent pairing versus nearest-neighbour disjoint pairing. The latter tests whether the main conclusions depend on communication locality rather than density alone.

## 4. Metrics and Operating-Envelope Definition

The principal metrics are mean link SINR, first-transmission success probability derived from TB BLER, expected delivered PHY goodput per link, Jain goodput fairness, co-channel interferer count, and a diagnostic decomposition of failed links into dominant-interferer, aggregate-interference, and noise-limited categories.

For the failure diagnostic, success below 0.5 is treated as a policy failure. This threshold is an experimental diagnostic choice, not a standard requirement.

For the operating envelope, a scenario is feasible under the explicit engineering policy:

- mean first-transmission success >= 0.10; and
- mean expected PHY goodput >= 1.0 Mbps.

For each (R,G), the envelope reports the **largest evaluated** swarm size satisfying both conditions. It is not a universal maximum swarm capacity.

## 5. Results

### 5.1 Density drives the baseline into a severe interference-limited regime

With one shared resource and no directional advantage, mean SINR decreases from -0.49 dB at N=5 to -23.03 dB at N=100. At N=100, first-transmission success is 0.0128 and expected PHY goodput is 0.359 Mbps. The high-density failure composition is dominated by aggregate interference: approximately 72.4% of policy-failed links are classified as aggregate-interference dominated, versus 27.6% as dominant-interferer failures. This indicates that the dense regime is primarily a many-interferer problem.

### 5.2 Exact resource separation with the primary allocator improves reliability despite its bandwidth cost

At N=100 and G=0 under the primary weighted conflict-graph assignment:

| Resources | Mean SINR (dB) | First-TX success | Expected goodput (Mbps) |
|---:|---:|---:|---:|
| 1 | -23.03 | 0.0128 | 0.359 |
| 2 | -16.20 | 0.0749 | 0.668 |
| 4 | -10.48 | 0.0775 | 0.572 |
| 8 | -5.47 | 0.2049 | 1.042 |

The non-monotonic goodput change between R=2 and R=4 is a central result rather than an anomaly. Increasing orthogonality improves SINR, but each additional partition also reduces per-link PRBs and TBS. Only when the interference reduction outweighs the bandwidth loss does expected goodput increase. Under the primary allocator, the R=8 case crosses the 1 Mbps target at N=100 despite using the narrowest per-link resource partitions. Section 5.6 explicitly separates this frequency-isolation effect from the additional gain of conflict-aware assignment.

### 5.3 Directionality alone is insufficient in the densest shared-resource case

At N=100 with R=1, increasing directional relative advantage from 0 to 9 dB changes mean SINR from -23.03 to -14.03 dB and expected goodput from 0.359 to 1.435 Mbps. First-transmission success nevertheless reaches only 0.0494, so the scenario still fails the explicit 0.10 reliability target. Goodput and reliability therefore need to be considered jointly.

### 5.4 Resource separation and spatial selectivity are complementary

At N=100:

| R | G (dB) | Mean SINR (dB) | First-TX success | Expected goodput (Mbps) |
|---:|---:|---:|---:|---:|
| 1 | 0 | -23.03 | 0.0128 | 0.359 |
| 8 | 0 | -5.47 | 0.2049 | 1.042 |
| 2 | 6 | -10.20 | 0.1262 | 1.414 |
| 4 | 6 | -4.48 | 0.2193 | 1.608 |
| 8 | 6 | 0.53 | 0.5292 | 2.229 |
| 8 | 9 | 3.53 | 0.8050 | 3.493 |

The matched-seed comparison between R=8,G=6 and the R=1,G=0 baseline at N=100 shows a first-transmission success increase of +0.516362. The Student-t 95% CI is [0.505703, 0.527021] and the deterministic bootstrap 95% CI is [0.505738, 0.526751], with Cohen dz=9.61 and Wilcoxon p=3.90e-18 (n=100). Expected PHY goodput increases by +1.870088 Mbps, with Student-t 95% CI [1.726815, 2.013360], bootstrap 95% CI [1.716869, 2.003005], dz=2.59, and Wilcoxon p=4.34e-17. These paired statistics are derived system-level comparisons across identical deterministic seeds; effect magnitudes and confidence intervals are the primary evidence.

### 5.5 Evaluated operating envelope for the primary controlled regime

Under the primary geometry-independent pairing and weighted conflict-graph allocator, and the explicit policy requiring first-transmission success >=0.10 and expected goodput >=1 Mbps, the largest evaluated feasible swarm sizes are:

| Resources R | G=0 dB | G=3 dB | G=6 dB | G=9 dB |
|---:|---:|---:|---:|---:|
| 1 | 10 | 10 | 20 | 50 |
| 2 | 50 | 75 | 100 | 100 |
| 4 | 50 | 75 | 100 | 100 |
| 8 | 100 | 100 | 100 | 100 |

The result should not be read as “100 UAVs are universally supported.” The evaluated grid is capped at N=100, and the envelope is conditioned on the primary pairing and allocator. Within that controlled regime, the feasible region shifts substantially when interference is reduced before BLER mapping. Moderate resource separation combined with moderate spatial selectivity can reach the same evaluated boundary as much stronger partitioning, while directionality alone on one shared resource does not. Section 5.6 quantifies how random assignment and local nearest-neighbour pairing change this boundary interpretation.

### 5.6 Allocation and pairing sensitivities bound the interpretation

The exact-resource results combine two mechanisms: fewer co-channel links from frequency partitioning and the primary weighted conflict-graph assignment. Matched-seed random assignment separates these effects. At N=100 and G=0, random allocation gives first-TX success / expected goodput of 0.0670 / 0.578 Mbps for R=2, 0.0511 / 0.374 Mbps for R=4, and 0.1463 / 0.815 Mbps for R=8. The conflict-graph allocator increases these to 0.0749 / 0.668, 0.0775 / 0.572, and 0.2049 / 1.042, respectively. For R=8, the matched first-TX success increase is +0.0586 with bootstrap 95% CI [0.0510, 0.0658], while expected goodput increases by +0.226 Mbps [0.186, 0.268]. Thus frequency isolation remains beneficial under random assignment, but the primary allocator contributes materially and is required for the R=8,G=0 point to cross the 1 Mbps policy threshold at N=100.

Pairing is an even stronger boundary condition. Under the primary geometry-independent pairing at N=100, the mean desired-link distance is 517.2 m and the shared-resource R=1,G=0 case yields -23.03 dB mean SINR, 0.0128 first-TX success, and 0.359 Mbps. Replacing only the pairing rule with nearest-neighbour disjoint pairing reduces mean desired distance to 84.0 m and changes those metrics to -1.75 dB, 0.4766, and 15.12 Mbps. The matched success difference is +0.4637 with bootstrap 95% CI [0.4539, 0.4736]. For R=8,G=6, nearest-neighbour pairing yields 0.9749 success and 15.00 Mbps versus 0.5292 and 2.229 Mbps under the primary pairing.

These results do not invalidate the primary density experiment: its geometry-independent pairing is deliberately useful for holding the desired-link distance distribution approximately invariant while interference grows with N. They do show that the resulting operating envelope is a controlled non-local-peer regime, not a universal statement about local swarm coordination. In a local-neighbour traffic regime, shorter desired links can compensate for much of the density penalty.

## 6. Discussion

### 6.1 Interference should be reduced before retransmission

The broader thesis campaign showed that when first-transmission TB BLER is already near one, idealized Chase-combining HARQ offers limited recovery while adding latency. This motivates treating retransmission as a supporting mechanism rather than the primary mitigation strategy in dense aerial sidelink. Resource isolation and spatial selectivity improve the underlying SINR before retransmission is considered.

### 6.2 Resource partitioning has a real cost

A model that removes co-channel interferers while leaving every link with all 133 PRBs would overstate the benefit of orthogonalization. Exact PRB partitioning exposes the actual trade-off between fewer interferers and smaller TBS/occupied bandwidth. The N=100 R=2 versus R=4 goodput result makes this cost visible and prevents the trivial conclusion that more orthogonal resources are always better.

### 6.3 Implications for aerial sidelink design

The results motivate mechanisms that jointly coordinate communication locality, resource reuse, and spatial selectivity. A practical distributed or centralized scheduler could account for both peer distance and local interference conditions when deciding whether additional orthogonal separation is worth its bandwidth cost. The allocator sensitivity shows that assignment policy matters even when the number of resources is fixed, while the pairing sensitivity shows that topology-aware selection of short desired links can dominate the absolute operating point. Directional arrays could then suppress residual co-channel interference. The present work does not claim to implement a standards-complete scheduler, peer-selection protocol, or beam-management procedure; it provides controlled operating-region evidence that separates these design levers.

## 7. Limitations

No measured multi-UAV RF interference, BLER, PDR, or end-to-end latency is claimed. The A2A propagation law is measurement-derived, but the simulated geometries and RF realizations are not measurements. Numerical BLER curves are 5G-LENA link-level simulation evidence. The study is not a bit-accurate or standards-complete sidelink PHY/MAC implementation. The conflict-graph resource allocator is a project abstraction rather than normative Mode 1/Mode 2 resource selection. The directional variable is an experimental desired/interferer sensitivity rather than full MIMO, beam tracking, or beam management. Full fast fading is not modeled. Transport-block BLER derived from code-block BLER assumes independent code-block decoding events.

The primary pairing is a controlled geometry-independent disjoint-peer abstraction selected to prevent desired-link distance from shrinking automatically as N increases; nearest-neighbour sensitivity demonstrates that local traffic produces much stronger absolute performance. The TBS-aware link adaptation is also a **THIS_WORK** model-based selection rule that chooses the available MCS maximizing expected first-transmission delivered bits per slot from the modeled SINR; it is not normative NR AMC and represents an informed link-adaptation abstraction. Broader project ablations include fixed-MCS comparisons, but the present paper focuses on the resource/directionality operating region. Finally, the envelope thresholds are explicit engineering-policy choices rather than 3GPP requirements, and the largest evaluated N is not a universal swarm-capacity limit.

## 8. Conclusion

Under a controlled geometry-independent peer-pairing regime, dense shared-resource UAV sidelink becomes severely interference-limited as swarm size increases, with high-density failures dominated by aggregate interference. Exact frequency-resource partitioning can recover substantial reliability after accounting for PRB/TBS and occupied-noise-bandwidth reduction, while directional spatial selectivity provides complementary gain. At N=100, R=8,G=6 improves first-transmission success by 0.5164 and expected PHY goodput by 1.870 Mbps relative to R=1,G=0 under matched seeds. Random-allocation baselines show that the conflict-graph assignment contributes materially but does not account for the entire frequency-isolation benefit.

The strongest qualification is communication locality: nearest-neighbour pairing changes the N=100 shared-resource baseline from 0.0128 to 0.4766 first-TX success by shortening the mean desired link from 517 m to 84 m. The principal conclusion is therefore conditional rather than universal: density, resource reuse, assignment policy, spatial selectivity, and peer-selection geometry jointly determine the feasible operating region. Future work should validate these trends with standards-complete sidelink resource selection and beam management, mobility-aware peer selection, full channel dynamics, and ultimately multi-UAV RF measurements.

## References

[1] D. Mishra, A. Trotta, E. Traversi, M. Di Felice, and E. Natalizio, “Cooperative Cellular UAV-to-Everything (C-U2X) communication based on 5G sidelink for UAV swarms,” *Computer Communications*, vol. 192, pp. 173–184, 2022. DOI: `10.1016/j.comcom.2022.06.001`.

[2] W. J. Lau, J. M.-Y. Lim, C. Y. Chong, N. S. Ho, and T. W. M. Ooi, “General Outage Probability Model for UAV-to-UAV links in Multi-UAV Networks,” *Computer Networks*, vol. 229, 109752, 2023. DOI: `10.1016/j.comnet.2023.109752`.

[3] M. Varonen, “Using NR Sidelink for UAV Swarm Internal Communication,” Master's thesis, Aalto University, 2024. URN: `URN:NBN:fi:aalto-202403172777`.

[4] M. M. Alam and S. Moh, “Joint Trajectory Control, Frequency Allocation, and Routing for UAV Swarm Networks: A Multi-Agent Deep Reinforcement Learning Approach,” *IEEE Transactions on Mobile Computing*, vol. 23, no. 12, pp. 11989–12005, 2024. DOI: `10.1109/TMC.2024.3403890`.

[5] A. Giannakoulas, N. Karkanis, S. Markou, G. Kyriacou, and T. Kaifas, “Sidelink Communication for Unmanned Platforms' (UxU) Swarms in Challenging Scenarios,” 6th International Conference on Communications, Information, Electronic and Energy Systems (CIEES), 2025. DOI: `10.1109/CIEES66347.2025.11300255`.

[6] H. Zhang, H.-M. Chen, Q.-J. Wei, Z.-W. Wang, and Y.-H. Sun, “Optimized Synchronization Design for UAV Swarm Network Based on Sidelink,” *Drones*, vol. 10, no. 4, 304, 2026. DOI: `10.3390/drones10040304`.

[7] U. Erdemir et al., “Measurement-based Channel Characterization for A2A and A2G Wireless Drone Communication Systems,” IEEE VTC 2023-Spring, 2023. DOI: `10.1109/VTC2023-Spring57618.2023.10199853`.

[8] N. Patriciello et al., “An E2E simulator for 5G NR networks,” *Simulation Modelling Practice and Theory*, vol. 96, 101933, 2019. DOI: `10.1016/j.simpat.2019.101933`.

[9] CTTC 5G-LENA v5.0 software archive. DOI: `10.5281/zenodo.21165297`.

[10] 3GPP TR 38.901 V19.4.0; 3GPP TR 36.777; 3GPP TS 38.211/38.212/38.213/38.214 and TS 38.104, project-recorded versions.

## Reproducibility and frozen evidence

The reviewer-hardened publication path uses the `paper-operating-envelope` workflow with the official 5G-LENA v5.0 Table-1 data, 100 matched deterministic seeds per primary scenario, exact PRB-subcarrier noise-bandwidth accounting, and separate matched-seed allocator/pairing sensitivities. The exact final submission freeze (git SHA, workflow run, artifact ID, digest, scenario counts, and audit status) is recorded in `docs/experiments/013_reviewer_hardened_publication_evidence.md`. Scientific results in this manuscript must match that record; older publication freezes are retained only for provenance.
