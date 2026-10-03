# Interference Scaling, Resource Isolation, and Topology Sensitivity in 5G NR Sidelink UAV Swarms

> **Submission draft.** All numerical RF/network results reported here are simulation/model-derived unless explicitly stated otherwise. The paper does not claim measured multi-UAV RF performance.

## Abstract

Direct NR sidelink is attractive for infrastructure-independent communication inside unmanned aerial vehicle (UAV) swarms, but the interference regime depends jointly on density, communication topology, resource reuse, and spatial selectivity. This paper presents a measurement-grounded, NR-aware system-level study using a published 3.5 GHz air-to-air path-loss fit, standards-based NR MCS/TBS/LDPC mechanics, and official 5G-LENA v5.0 SINR-to-BLER data. A 100-seed baseline campaign evaluates 5–100 UAVs, exact partitions of a 133-PRB 50 MHz / 30 kHz profile into 1/2/4/8 resources, and an experimental 0–9 dB desired/interferer directional relative advantage. Under the baseline full-load sequential-disjoint topology, mean SINR falls to -23.03 dB at 100 UAVs; first-transmission success is 0.0128 and expected PHY goodput is 0.359 Mbps. At the same N, R=8,G=6 yields 0.5292 success and 2.229 Mbps, with matched-seed differences of +0.5164 success and +1.870 Mbps goodput. A separate 100-seed robustness campaign shows that topology is critical: nearest-neighbour pairing at N=100,R=1,G=0 shortens the mean desired link from 517 m to 84 m and increases success to 0.4766 and goodput to 15.116 Mbps. Random-allocation and fixed-MCS checks also reduce performance relative to the main allocator/adaptation assumptions, whereas exact PRB-noise-bandwidth accounting has negligible impact in the evaluated interference regimes. The results therefore characterize topology-dependent operating regions rather than a universal swarm-capacity limit.

## 1. Introduction

UAV swarms require frequent exchange of position, status, control, coordination, and mission information. Direct device-to-device communication is attractive because swarm operation may occur outside reliable infrastructure coverage and because local coordination traffic should not necessarily traverse a base station. NR sidelink provides a standardized direct-transmission framework and is therefore a natural candidate for intra-swarm communication.

Aerial propagation creates a difficult interference regime. Strong line-of-sight conditions benefit the desired link but can also strengthen many simultaneous interferers. As swarm density grows, a shared sidelink resource can transition from sparse interference to aggregate-interference domination. Retransmission does not remove this root cause when first-transmission BLER is already near one. Frequency orthogonalization can reduce the number of co-channel interferers, but it also reduces the PRBs and transport-block size available to each transmission. Directional transmission can further improve the desired-to-interference balance, although its value depends on the level of resource isolation already present.

This paper asks:

> **How do swarm density and communication topology change the NR sidelink interference regime, and how far can resource separation and directional spatial selectivity extend the feasible reliability/goodput operating region?**

The paper makes three contributions. First, it provides a measurement-grounded, NR-aware system evaluation that combines a published 3.5 GHz A2A path-loss fit, standards-based NR transport-block mechanics, and sourced 5G-LENA v5.0 BLER curves. Second, it quantifies the interference and reliability/goodput operating region under a controlled full-load baseline while explicitly accounting for the PRB/TBS cost of resource partitioning and experimental spatial selectivity. Third, it performs a matched-seed robustness analysis over communication pairing, resource-allocation policy, link adaptation, and noise-bandwidth accounting, showing which conclusions are topology-dependent and which remain stable across modeling choices.

The study is intentionally system-level. It does not claim a bit-accurate NR sidelink PHY, normative Mode-1/Mode-2 scheduling, measured swarm PDR/BLER/latency, or full MIMO/beam-management behavior.

## 2. Related Work

Mishra et al. studied cooperative C-U2X communication based on 5G sidelink for UAV swarms, emphasizing multi-hop communication and communication-aware channel scheduling [1]. Their work establishes the relevance of sidelink to UAV swarm networking, while the present study focuses on a density-resource-directionality operating envelope with NR TBS/LDPC-aware link evaluation.

Lau et al. derived a general analytical outage model for U2U links in multi-UAV networks and evaluated the effect of network parameters on SINR, outage probability, and capacity-related metrics [2]. Their analytical characterization is complementary to the present approach, which maps system SINR through sourced NR-oriented link-level BLER curves and exact transport-block/resource mechanics.

Varonen evaluated NR sidelink for UAV swarm internal communication and studied routing-update requirements [3]. The present work moves from suitability analysis toward quantitative dense-swarm operating-region characterization.

Recent UAV-swarm research has also emphasized joint optimization of trajectory, frequency allocation, and routing using multi-agent learning [4]. The goal here is different: resource assignment is deliberately kept as an auditable system-level abstraction so that density, bandwidth partitioning, and spatial selectivity can be isolated rather than hidden inside an optimizer.

Giannakoulas et al. reported sidelink communication for unmanned-platform swarms in challenging scenarios [5], while Zhang et al. recently addressed UAV-swarm sidelink synchronization and Doppler-related access/synchronization design [6]. These works reinforce that sidelink UAV swarms are an active research area, but they target different protocol and system questions.

A concise comparison of the closest work is shown below. The table is descriptive rather than a quality ranking.

| Work | Main method/question | NR-aware TBS/BLER mechanics | Dense-swarm interference scaling | Explicit resource-bandwidth trade-off | Resource + spatial-selectivity operating envelope |
|---|---|---:|---:|---:|---:|
| Mishra et al. [1] | Cooperative C-U2X / multi-hop and scheduling | Different focus | Partial/different focus | No | No |
| Lau et al. [2] | Analytical U2U outage characterization | No | Yes, analytically | No | No |
| Varonen [3] | NR sidelink suitability / routing updates | Different focus | Limited | No | No |
| This work | Controlled system-level operating-region characterization | Yes, sourced/standards-based mechanics | Yes | Yes | Yes |

The contribution of this paper is therefore not the generic use of sidelink in UAV swarms. It is a reproducible, measurement-grounded and NR-aware characterization of how density, exact resource isolation, and directional selectivity jointly shape the evaluated reliability/goodput operating region. The claim is deliberately limited to the evaluated system-level abstractions and does not imply standards-complete NR sidelink behavior.

## 3. System Model and Scientific Provenance

### 3.1 Air-to-air propagation

The baseline large-scale A2A channel uses the fitted path-loss model reported by Erdemir et al. at 3.5 GHz [7]:

`PL(d) = 34.650 + 10 * 2.166 * log10(d / 1 m)`.

The coefficients are derived fitted parameters from a published measurement campaign, not raw samples. RF values produced at arbitrary simulated distances are therefore derived from a measurement-based model and must not be interpreted as field measurements.

### 3.2 NR resource profile and transport-block mechanics

The evaluated profile uses 3.5 GHz carrier frequency, 50 MHz channel bandwidth, 30 kHz subcarrier spacing, 133 PRBs, and 0.5 ms slots. NR MCS Table-1 parameters, TBS quantization, LDPC base-graph selection, and code-block segmentation follow the project implementation of Release-19 rules. The selected PSCCH/PSSCH/guard/DM-RS overhead profile is an explicit study configuration rather than a universal sidelink resource-pool requirement.

### 3.3 BLER evidence

For each candidate MCS, the computed TBS determines LDPC base graph and nominal code-block size. The request is mapped to the closest sourced 5G-LENA v5.0 curve for the same MCS/base graph, and transport-block BLER is derived from code-block BLER under an independent-code-block approximation. Link adaptation is a `THIS_WORK` system-level abstraction: for the instantaneous modeled SINR, the implementation selects the available MCS that maximizes expected first-transmission delivered bits per slot. It is not normative 3GPP AMC and assumes idealized instantaneous link-state knowledge. A fixed-MCS robustness check is therefore included in the reviewer-sensitivity campaign.

The canonical publication run used the official CTTC 5G-LENA v5.0 Table-1 source: release short commit `47a3adc2`, DOI `10.5281/zenodo.21165297`, 1,332 sourced curves, BG1/BG2, and MCS 0–28. These numerical curves are **LINK_LEVEL_SIMULATION** evidence; they are neither UAV field measurements nor 3GPP-standard BLER tables.

### 3.4 Exact resource partitioning

The 133 PRBs are partitioned as evenly as possible:

- R=1: 133 PRBs;
- R=2: 67+66;
- R=4: 34+33+33+33;
- R=8: 17+17+17+17+17+16+16+16.

Links on different abstract frequency resources do not interfere in the system model. For every assigned resource, TBS, LDPC segmentation, requested CBS, and sourced BLER mapping are recomputed. In the frozen publication experiment, effective noise bandwidth is scaled by the assigned PRB share of the nominal 50 MHz channel, i.e. `50 MHz × N_PRB/133`. This preserves the original frozen evidence semantics. A separate robustness campaign uses the exact occupied OFDM bandwidth `N_PRB × 12 × 30 kHz` (47.88 MHz for 133 PRBs) to test sensitivity to this approximately 0.19 dB full-band noise-accounting difference. Resource separation is therefore not modeled as free interference removal while retaining the full payload resource.

Resource assignment uses a weighted conflict-graph heuristic developed in this project. The weight between links `i` and `j` is a symmetric geometry-only proxy proportional to `1/d(Tx_i,Rx_j)^2 + 1/d(Tx_j,Rx_i)^2`; links are greedily assigned to the resource with minimum accumulated conflict weight. This is **THIS_WORK**, not normative NR sidelink Mode-1/Mode-2 sensing or scheduling. A seeded random allocation is included as a no-coordination robustness baseline at the same `(N,R,G)`.

### 3.5 Directionality abstraction

The experimental directional relative advantage `G` in {0,3,6,9} dB is implemented as `+G/2` dB on the desired link and `-G/2` dB on co-channel interference. The relative desired/interferer advantage is therefore `G` dB. This is an **EXPERIMENTAL_SWEEP** sensitivity variable, not a measured antenna gain or full MIMO/beam-management model.

### 3.6 Geometry, traffic activity, and Monte Carlo design

The baseline geometry places UAVs independently and uniformly over a 1000 m × 1000 m horizontal area at a common altitude of 100 m. Carrier frequency is 3.5 GHz, transmit power is 30 dBm, receiver noise figure is 7 dB, and all disjoint links are active simultaneously (activity probability 1.0). The baseline pairing is deterministic index-based disjoint pairing `(0,1),(2,3),...`; it is a controlled topology abstraction, not a claim that operational swarms pair arbitrary nodes this way.

The campaign evaluates N={5,10,20,30,50,75,100} UAVs. Each full (N,R,G) point uses 100 deterministic matched seeds. The full campaign contains 11,200 per-seed realizations and 112 scenario summaries. The same seed is reused across compared `(R,G)` configurations so that geometry is matched.

| Parameter | Baseline value | Scientific status |
|---|---:|---|
| Horizontal deployment area | 1000 m × 1000 m | Experimental configuration |
| Altitude | 100 m | Experimental configuration |
| Carrier frequency | 3.5 GHz | Study profile / channel-source match |
| Nominal channel bandwidth | 50 MHz | Study profile |
| SCS | 30 kHz | Study profile |
| PRBs | 133 | NR FR1 profile |
| Tx power | 30 dBm | Experimental configuration |
| Noise figure | 7 dB | Experimental configuration |
| Activity probability | 1.0 | Full-load stress configuration |
| Baseline pairing | Sequential disjoint | THIS_WORK topology abstraction |
| Baseline resource allocator | Weighted conflict graph | THIS_WORK |
| Directional relative advantage | 0/3/6/9 dB | Experimental sweep |
| Seeds per main scenario | 100 | Monte Carlo design |

### 3.7 Reviewer-facing robustness design

A separate robustness campaign, which does not overwrite the frozen main evidence, tests four modeling choices: (i) sequential versus nearest-neighbour disjoint pairing; (ii) weighted conflict-graph versus seeded random allocation; (iii) adaptive expected-goodput-maximizing MCS versus a fixed MCS-4 baseline; and (iv) exact PRB occupied-noise bandwidth rather than nominal-channel-share noise bandwidth. The robustness grid uses N={20,50,100}, R={1,4,8}, and G={0,6} dB with matched deterministic seeds. These checks are intended to establish whether the qualitative density/interference conclusions depend on one convenient abstraction.

Numerical robustness claims must be taken only from a successful committed `paper_robustness` workflow output; this manuscript does not pre-commit to their direction or magnitude.

## 4. Metrics and Operating-Envelope Definition

The principal metrics are mean link SINR, first-transmission success probability derived from TB BLER, expected delivered PHY goodput per link, Jain goodput fairness, co-channel interferer count, and a diagnostic decomposition of failed links into dominant-interferer, aggregate-interference, and noise-limited categories.

For the failure diagnostic, success below 0.5 is treated as a policy failure. This threshold is an experimental diagnostic choice, not a standard requirement.

For the operating envelope, a scenario is feasible under the explicit engineering policy:

- mean first-transmission success >= 0.10; and
- mean expected PHY goodput >= 1.0 Mbps.

For each (R,G), the envelope reports the **largest evaluated** swarm size satisfying both conditions. It is not a universal maximum swarm capacity.

## 5. Results

### 5.1 The full-load long-link baseline enters a severe interference-limited regime

Under the baseline sequential-disjoint pairing, desired transmitter/receiver identities are independent of spatial proximity, producing a mean desired-link distance of approximately 517 m at N=100. With one shared resource and no directional advantage, mean SINR decreases from -0.49 dB at N=5 to -23.03 dB at N=100. At N=100, first-transmission success is 0.0128 and expected PHY goodput is 0.359 Mbps. The high-density failure composition is dominated by aggregate interference: approximately 72.4% of policy-failed links are classified as aggregate-interference dominated, versus 27.6% as dominant-interferer failures. This is a baseline-topology result rather than evidence that density alone universally causes such collapse.

### 5.2 Exact resource separation improves reliability despite its bandwidth cost

At N=100 and G=0:

| Resources | Mean SINR (dB) | First-TX success | Expected goodput (Mbps) |
|---:|---:|---:|---:|
| 1 | -23.03 | 0.0128 | 0.359 |
| 2 | -16.20 | 0.0749 | 0.668 |
| 4 | -10.48 | 0.0775 | 0.572 |
| 8 | -5.47 | 0.2049 | 1.042 |

The non-monotonic goodput change between R=2 and R=4 is a central result rather than an anomaly. Increasing orthogonality improves SINR, but each additional partition also reduces per-link PRBs and TBS. Only when the interference reduction outweighs the bandwidth loss does expected goodput increase. The R=8 case crosses the 1 Mbps target at N=100 despite using the narrowest per-link resource partitions.

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

The matched-seed comparison between R=8,G=6 and the R=1,G=0 baseline at N=100 shows a first-transmission success increase of +0.516358 with normal-approximation 95% CI [0.505829, 0.526887] and Cohen dz=9.6122 (n=100). Expected PHY goodput increases by +1.870079 Mbps with normal-approximation 95% CI [1.728555, 2.011603] and dz=2.5899 (n=100). The analysis pipeline additionally reports deterministic paired-bootstrap percentile 95% confidence intervals for the matched differences; these should be used as the primary robustness check for bounded/non-Gaussian metrics in the final formatted paper. Paired t-test p-values are retained in the artifact as secondary diagnostics rather than emphasized as the main evidence. These paired statistics are derived system-level comparisons across identical deterministic seeds.

### 5.5 Evaluated operating envelope

Under the explicit policy requiring first-transmission success >=0.10 and expected goodput >=1 Mbps, the largest evaluated feasible swarm sizes are:

| Resources R | G=0 dB | G=3 dB | G=6 dB | G=9 dB |
|---:|---:|---:|---:|---:|
| 1 | 10 | 10 | 20 | 50 |
| 2 | 50 | 75 | 100 | 100 |
| 4 | 50 | 75 | 100 | 100 |
| 8 | 100 | 100 | 100 | 100 |

The result should not be read as “100 UAVs are universally supported.” The evaluated grid is capped at N=100. The finding is that the feasible region shifts substantially when interference is reduced before BLER mapping. Moderate resource separation combined with moderate spatial selectivity can reach the same evaluated boundary as much stronger partitioning, while directionality alone on one shared resource does not.

### 5.6 Robustness: topology dominates the baseline regime, while allocator and adaptation remain material

The reviewer-facing 100-seed robustness campaign changes one modeling dimension at a time while preserving the same propagation and NR link-evaluation evidence. The strongest sensitivity is communication topology. At N=100,R=1,G=0, replacing sequential disjoint pairing by nearest-neighbour disjoint pairing reduces mean desired-link distance from 517.20 m to 84.05 m. Mean SINR changes from -23.03 dB (95% CI [-23.21,-22.84]) to -1.75 dB ([-1.89,-1.61]), first-TX success from 0.0128 ([0.0104,0.0153]) to 0.4766 ([0.4668,0.4863]), and expected goodput from 0.359 Mbps ([0.224,0.494]) to 15.116 Mbps ([14.497,15.736]). Thus, the headline density collapse is not topology invariant: maintaining short desired links can preserve a much healthier shared-resource operating point even at high N.

Resource coordination remains beneficial within either topology. At N=100,R=8,G=0 with sequential pairing, the weighted conflict-graph allocator gives success 0.2049 and goodput 1.042 Mbps, versus 0.1463 and 0.815 Mbps for seeded random allocation. With nearest-neighbour pairing, the corresponding values are 0.9465/10.836 Mbps versus 0.8824/8.357 Mbps. This separates the benefit of having multiple resources from the additional benefit of geometry-aware reuse.

Link adaptation is also material. At N=100,R=8,G=6 under sequential pairing, adaptive MCS gives success 0.5292 and goodput 2.229 Mbps, whereas fixed MCS-4 gives 0.3309 and 0.722 Mbps. The paper therefore treats the adaptive-MCS result as an optimistic system-level control assumption rather than a normative AMC implementation.

Finally, replacing nominal-channel PRB-share noise accounting with exact occupied PRB bandwidth changes mean SINR by at most 0.113 dB over the overlapping robustness grid, first-TX success by less than 7.4e-5, and expected goodput by less than 3.1e-4 Mbps. The main qualitative conclusions are therefore insensitive to this bandwidth-accounting convention in the evaluated interference regimes.

## 6. Discussion

### 6.1 Interference should be reduced before retransmission

The broader thesis campaign showed that when first-transmission TB BLER is already near one, idealized Chase-combining HARQ offers limited recovery while adding latency. This motivates treating retransmission as a supporting mechanism rather than the primary mitigation strategy in dense aerial sidelink. Resource isolation and spatial selectivity improve the underlying SINR before retransmission is considered.

### 6.2 Resource partitioning has a real cost

A model that removes co-channel interferers while leaving every link with all 133 PRBs would overstate the benefit of orthogonalization. Exact PRB partitioning exposes the actual trade-off between fewer interferers and smaller TBS/occupied bandwidth. The N=100 R=2 versus R=4 goodput result makes this cost visible and prevents the trivial conclusion that more orthogonal resources are always better.

### 6.3 Topology control is a first-order interference-management mechanism

The nearest-neighbour sensitivity shows that swarm density cannot be interpreted independently of desired-link geometry. Increasing N while preserving arbitrary long desired links produces a very different SINR distribution from increasing N while allowing each node to communicate locally. In practice, clustering, neighbor selection, relay selection, or topology-aware pairing can therefore be as important as frequency partitioning. The operating envelope should consequently be parameterized by communication topology rather than treated as a function of N alone.

### 6.4 Implications for aerial sidelink design

The results motivate mechanisms that jointly coordinate resource reuse and exploit spatial selectivity. A practical distributed or centralized scheduler could estimate local interference conditions and select whether additional orthogonal separation is worth its bandwidth cost. Directional arrays could then suppress the residual co-channel interference. The present work does not claim to implement such a standards-complete scheduler or beam-management procedure; it provides the operating-region characterization needed to motivate and evaluate them.

## 7. Limitations

No measured multi-UAV RF interference, BLER, PDR, or end-to-end latency is claimed. The A2A propagation law is measurement-derived, but the simulated geometries and RF realizations are not measurements. Numerical BLER curves are 5G-LENA link-level simulation evidence. The study is not a bit-accurate or standards-complete sidelink PHY/MAC implementation. The conflict-graph resource allocator is a project abstraction rather than normative Mode 1/Mode 2 resource selection. The directional variable is an experimental desired/interferer sensitivity rather than full MIMO, beam tracking, or beam management. Full fast fading is not modeled. Baseline pairing is a deterministic disjoint abstraction and baseline link adaptation uses idealized instantaneous modeled SINR; both are explicitly tested in the separate robustness campaign. Transport-block BLER derived from code-block BLER assumes independent code-block decoding events. The frozen main campaign uses nominal-channel-share noise bandwidth when PRBs are partitioned, while the robustness campaign tests exact PRB occupied bandwidth. The envelope thresholds are explicit engineering-policy choices rather than 3GPP requirements, and the largest evaluated N is not a universal swarm-capacity limit.

## 8. Conclusion

Under the evaluated full-load sequential-disjoint topology, dense shared-resource UAV sidelink becomes severely interference-limited, and exact resource partitioning plus directional relative advantage substantially expand the evaluated reliability/goodput operating region. At N=100, R=8,G=6 improves first-transmission success by 0.5164 and expected PHY goodput by 1.870 Mbps relative to that baseline under matched seeds. The robustness campaign, however, shows that this collapse is not a density-only law: nearest-neighbour pairing at N=100 shortens desired links enough to raise shared-resource success from 0.0128 to 0.4766 and goodput from 0.359 to 15.116 Mbps. Geometry-aware resource allocation and adaptive MCS provide additional gains, while exact PRB-noise-bandwidth accounting has negligible effect in the evaluated interference regimes. The central design implication is therefore broader than resource partitioning alone: dense aerial sidelink should jointly control communication topology, resource reuse, spatial selectivity, and link adaptation. Future work should validate these topology-dependent operating regions with standards-complete sidelink procedures, realistic beam management/fast fading, and ultimately multi-UAV RF measurements.

## References

[1] D. Mishra, A. Trotta, E. Traversi, M. Di Felice, and E. Natalizio, “Cooperative Cellular UAV-to-Everything (C-U2X) communication based on 5G sidelink for UAV swarms,” *Computer Communications*, vol. 192, pp. 173–184, 2022. DOI: `10.1016/j.comcom.2022.06.001`.

[2] W. J. Lau, J. M.-Y. Lim, C. Y. Chong, N. S. Ho, and T. W. M. Ooi, “General Outage Probability Model for UAV-to-UAV links in Multi-UAV Networks,” *Computer Networks*, vol. 229, 109752, 2023. DOI: `10.1016/j.comnet.2023.109752`.

[3] M. Varonen, “Using NR Sidelink for UAV Swarm Internal Communication,” Master's thesis, Aalto University, 2024. URN: `URN:NBN:fi:aalto-202403172777`.

[4] “Joint Trajectory Control, Frequency Allocation, and Routing for UAV Swarm Networks: A Multi-Agent Deep Reinforcement Learning Approach,” *IEEE Transactions on Mobile Computing*, vol. 23, no. 12, pp. 11989–12005, 2024. DOI: `10.1109/TMC.2024.3403890`.

[5] A. Giannakoulas et al., “Sidelink Communication for Unmanned Platforms' (UxU) Swarms in Challenging Scenarios,” 6th International Conference on Communications, Information, Electronic and Energy Systems (CIEES), 2025. DOI: `10.1109/CIEES66347.2025.11300255`.

[6] H. Zhang, H.-M. Chen, Q.-J. Wei, Z.-W. Wang, and Y.-H. Sun, “Optimized Synchronization Design for UAV Swarm Network Based on Sidelink,” *Drones*, vol. 10, no. 4, 304, 2026. DOI: `10.3390/drones10040304`.

[7] U. Erdemir et al., “Measurement-based Channel Characterization for A2A and A2G Wireless Drone Communication Systems,” IEEE VTC 2023-Spring, 2023. DOI: `10.1109/VTC2023-Spring57618.2023.10199853`.

[8] N. Patriciello et al., “An E2E simulator for 5G NR networks,” *Simulation Modelling Practice and Theory*, vol. 96, 101933, 2019. DOI: `10.1016/j.simpat.2019.101933`.

[9] CTTC 5G-LENA v5.0 software archive. DOI: `10.5281/zenodo.21165297`.

[10] 3GPP TR 38.901 V19.4.0; 3GPP TR 36.777; 3GPP TS 38.211/38.212/38.213/38.214 and TS 38.104, project-recorded versions.

## Reproducibility and current evidence

The current submission evidence was regenerated successfully on commit `f224ba9e5f95a23a088db24479c67461fcf497e6` by GitHub Actions workflow `paper-operating-envelope` run #26 (run ID `37106664614`). The uploaded artifact is `paper-operating-envelope-f224ba9e5f95a23a088db24479c67461fcf497e6`, artifact ID `11267104157`, digest `sha256:f3e6fe8ffac63168d878447bfd61f297f442a55c20b742e4def0374027350099`.

The artifact contains the 100-seed operating-envelope tables, paired normal and bootstrap confidence intervals, figures, the exact submission manuscript, claim guardrails, and the 100-seed reviewer robustness tables under `results/paper_robustness/`. The historical publication freeze in `docs/experiments/012_publication_evidence.md` remains preserved for provenance; the new robustness evidence is documented under `docs/experiments/013_reviewer_robustness.md`.