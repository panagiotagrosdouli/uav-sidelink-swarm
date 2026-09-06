# Interference Scaling and Cross-Layer Mitigation in 5G NR Sidelink UAV Swarms

> **Manuscript status:** research draft. Numerical results below are from the committed 100-seed publication campaign and are simulation/model-derived unless explicitly stated otherwise. This draft does not claim measured swarm RF performance.

## Abstract

Direct 5G NR sidelink is a promising mechanism for infrastructure-independent communication inside unmanned aerial vehicle (UAV) swarms, but dense line-of-sight aerial deployments can become strongly interference-limited. This work characterizes that scaling problem and quantifies how frequency-resource separation and directional spatial selectivity shift the feasible operating region. The system model combines a 3.5 GHz air-to-air propagation fit derived from a published UAV measurement campaign, standards-based NR MCS/TBS/LDPC mechanics, and numerical SINR-to-BLER curves processed from the official 5G-LENA v5.0 link-level dataset. A 100-seed system-level campaign evaluates swarm sizes from 5 to 100 UAVs, exact partitions of a 133-PRB 50 MHz / 30 kHz resource profile into 1, 2, 4, or 8 orthogonal frequency resources, and an experimental 0–9 dB directional relative desired/interference advantage. With one shared resource and no directional advantage, mean SINR degrades from -0.49 dB at 5 UAVs to -23.03 dB at 100 UAVs; at 100 UAVs the corresponding first-transmission success probability and expected goodput are 0.0128 and 0.359 Mbps. Exact resource partitioning provides substantial interference relief despite reducing per-link bandwidth: at 100 UAVs, eight resources without directional gain increase first-transmission success to 0.205 and expected goodput to 1.042 Mbps. Combining eight resources with a 6 dB experimental relative directional advantage yields 0.529 first-transmission success and 2.229 Mbps expected goodput. Under an explicit engineering policy requiring first-transmission success >= 0.10 and goodput >= 1 Mbps, the largest evaluated swarm size increases from 10 UAVs for the baseline to 100 UAVs for either eight resources without directional gain or two resources with a 6 dB relative directional advantage. These operating-envelope points are not universal capacity limits; rather, they quantify the cross-layer trade-off between interference isolation, available bandwidth, and spatial selectivity under the evaluated model. The results indicate that dense sidelink UAV swarms require interference-management mechanisms that act before retransmission, and motivate joint resource coordination and directional transmission for future aerial sidelink systems.

## 1. Introduction

UAV swarms rely on frequent exchange of state, control, coordination, and mission information. Infrastructure-independent direct communication is attractive because swarm operation may occur outside reliable cellular coverage or may require low-latency local exchange that should not traverse a base station. NR sidelink provides a standardized direct-transmission framework and has therefore attracted interest for UAV swarm internal communications.

The fundamental difficulty is that aerial links often experience strong line-of-sight propagation not only on the desired link but also from simultaneous transmitters. As swarm size grows, a shared sidelink resource can therefore transition from a sparse-interference regime to aggregate-interference domination. Merely adding retransmissions does not address the root cause when first-transmission BLER is already close to one. Conversely, splitting spectrum into more orthogonal resources reduces co-channel interference but also reduces the PRBs, transport-block size, and occupied bandwidth available to each transmission. Directional transmission can further improve the desired-to-interference balance, but its benefit depends on how much resource isolation is already present.

This paper focuses on that cross-layer operating-region question rather than proposing another routing or machine-learning optimizer:

> **How does UAV swarm density change the interference regime of NR sidelink, and how far can frequency-resource separation and directional spatial selectivity extend the feasible reliability/goodput operating region?**

The contributions are:

1. **Measurement-grounded, NR-aware system evaluation.** The large-scale A2A propagation baseline uses the fitted 3.5 GHz model reported by Erdemir et al.; NR MCS/TBS/LDPC mechanics are standards-based; numerical BLER evidence is taken from processed official 5G-LENA v5.0 link-level curves rather than an invented SINR threshold.
2. **Density-dependent interference characterization.** The campaign quantifies SINR, first-transmission success, expected goodput, fairness, co-channel interferer count, and dominant-versus-aggregate failure composition from 5 to 100 UAVs.
3. **Exact-resource operating envelope.** The 133-PRB profile is partitioned exactly across 1/2/4/8 orthogonal frequency resources, with occupied noise bandwidth and TBS/LDPC/CBS recomputed per partition. Combining this with a directional relative-advantage sweep yields an evaluated operating envelope under explicit reliability/goodput targets.

The study is intentionally system-level. It does not claim a bit-accurate sidelink PHY, normative Mode-1/Mode-2 scheduling, measured swarm PDR, or full MIMO/beam-management behavior.

## 2. Related Work

Mishra et al. studied cooperative cellular UAV-to-everything communication using 5G sidelink for UAV swarms, with emphasis on multi-hop communication and communication-aware channel scheduling. Their work establishes that sidelink is relevant to UAV swarm networking, but its primary contribution is scheduling/network formation rather than an NR TBS/LDPC-aware density-resource-directionality operating-envelope characterization [1].

Lau et al. derived a general analytical outage model for U2U links in multi-UAV networks and studied how network parameters affect SINR, outage probability, and channel-capacity metrics for arbitrary node locations [2]. That analysis provides an important interference-characterization baseline. The present work is complementary: rather than deriving a general closed-form outage distribution, it maps system SINR through sourced NR-oriented link-level BLER curves and standards-based transport-block mechanics, then evaluates the bandwidth/interference trade-off introduced by exact PRB partitioning.

Varonen evaluated the suitability of NR sidelink for UAV swarm internal communications and simulated routing-update requirements. The thesis concluded that sidelink provides favorable physical/link-layer procedures while leaving higher-layer functions such as routing/network management and some beamforming-related needs outside the standard's direct scope [3]. The present study moves from suitability assessment to quantitative dense-swarm operating-region characterization.

Recent UAV-swarm work has also emphasized joint optimization. The JTFR approach jointly optimizes trajectory, frequency allocation, and routing using multi-agent deep reinforcement learning and targets end-to-end delay, packet delivery, and energy [4]. This is a different objective from the present study: here, resource allocation is deliberately kept as an auditable system-level abstraction so that the effect of density, exact resource partition, and directional advantage can be isolated.

Giannakoulas et al. reported sidelink communication for unmanned-platform swarms in challenging scenarios [5]. Because only bibliographic metadata/abstract-level evidence has been verified for this work in the current literature audit, this manuscript does not make detailed comparative claims about its implementation.

More recently, Zhang et al. addressed UAV-swarm sidelink synchronization and Doppler-related access/synchronization design, including an A-NOMA-enhanced random-access framework [6]. Their contribution is protocol/synchronization focused and therefore orthogonal to the interference operating-envelope question studied here.

Taken together, prior work establishes UAV-swarm interference, sidelink feasibility, scheduling/routing, optimization, and synchronization as active topics. The contribution here is a reproducible, measurement-grounded and NR-aware characterization of how density, exact frequency-resource isolation, and spatial selectivity jointly determine the evaluated reliability/goodput operating region.

## 3. System Model and Scientific Provenance

### 3.1 A2A propagation

The baseline channel uses the published A2A large-scale path-loss fit from Erdemir et al. at 3.5 GHz:

`PL(d) = 34.650 + 10 * 2.166 * log10(d / 1 m)`.

The coefficients are fitted/derived parameters from the reported measurement campaign, not raw channel samples. RF values generated at arbitrary simulated distances are therefore **derived from a measurement-based model**, not measurements themselves.

### 3.2 NR resource profile

The evaluated profile uses:

- carrier frequency: 3.5 GHz;
- channel bandwidth: 50 MHz;
- SCS: 30 kHz;
- total PRBs: 133;
- slot duration: 0.5 ms;
- one transmission layer;
- explicit study configuration for PSCCH/PSSCH/guard/DM-RS overhead.

The 133-PRB bandwidth/SCS combination and NR transport-block mechanics are standards-based. The particular sidelink overhead profile is an explicit study configuration rather than a universal 3GPP resource-pool requirement.

### 3.3 Link adaptation and BLER provenance

NR MCS Table-1 parameters, TBS quantization, LDPC base-graph selection, and code-block segmentation follow the implemented Release-19 specification rules. For each candidate MCS, the computed TBS determines LDPC base graph and nominal code-block size. The system maps this request to the closest sourced 5G-LENA v5.0 curve for the same MCS/base graph, then derives transport-block BLER assuming independent code-block decoding events.

The full publication campaign processed the official 5G-LENA v5.0 Table-1 source at runtime:

- release: v5.0;
- release commit: `47a3adc2`;
- DOI: `10.5281/zenodo.21165297`;
- 1,332 sourced curves;
- base graphs 1 and 2;
- MCS indices 0–28.

These numerical BLER curves are **LINK_LEVEL_SIMULATION** evidence. They are neither UAV field measurements nor 3GPP-standard BLER tables.

### 3.4 Resource partitioning

For `R` orthogonal frequency resources, the 133 PRBs are divided as evenly as possible:

- R=1: `133`;
- R=2: `67+66`;
- R=4: `34+33+33+33`;
- R=8: `17+17+17+17+17+16+16+16`.

Links assigned different resources do not interfere in the system abstraction. For every assigned resource, the model recomputes occupied noise bandwidth, TBS, LDPC segmentation, requested CBS, and sourced BLER mapping. Thus resource separation is not treated as a free interference reduction while retaining the full 50 MHz payload resource.

Resource assignment uses a conflict-graph heuristic developed in this project. It is **THIS_WORK** and is not a normative NR sidelink Mode-1/Mode-2 scheduler.

### 3.5 Directionality abstraction

A directional relative advantage `G` in `{0,3,6,9}` dB is applied as:

- desired-link gain: `+G/2` dB;
- co-channel interference gain: `-G/2` dB.

Therefore the desired/interferer relative power advantage is `G` dB. This is an **EXPERIMENTAL_SWEEP** sensitivity abstraction. It is not a claim of measured antenna gain or a complete MIMO/beam-management implementation.

### 3.6 Swarm geometry and Monte Carlo design

The campaign evaluates `N = {5,10,20,30,50,75,100}` UAVs using deterministic Monte Carlo seeds. Transmitter/receiver pairs are disjoint to avoid artificial self-interference. Each full `(N,R,G)` point uses 100 matched seeds, enabling paired comparisons across mitigation configurations.

## 4. Metrics and Operating-Envelope Definition

The principal metrics are:

- mean link SINR;
- first-transmission success probability derived from TB BLER;
- expected delivered PHY goodput per link;
- Jain goodput fairness;
- number of co-channel interferers;
- failed-link decomposition into dominant-interferer, aggregate-interference, or noise-limited categories.

For the failure diagnostic, a link with first-transmission success below 0.5 is considered a policy failure. This threshold is an experimental diagnostic choice, not a standard requirement.

For the operating envelope, a scenario is marked feasible under the explicit engineering policy:

- mean first-transmission success >= 0.10; and
- mean expected goodput >= 1.0 Mbps.

For each `(R,G)` pair, the operating-envelope metric is the **largest evaluated swarm size** satisfying both conditions. It must not be interpreted as a universal maximum swarm capacity.

## 5. Results

### 5.1 Baseline density scaling

With one shared resource and no directional advantage, performance deteriorates strongly with swarm size. Mean SINR is -0.49 dB at N=5 and -23.03 dB at N=100. In the full-v5 publication evaluation, first-transmission success at N=100 is 0.0128 and expected goodput is 0.359 Mbps.

The failure composition also shifts toward aggregate interference. At N=100, approximately 72.4% of policy-failed links are classified as aggregate-interference dominated and 27.6% as dominant-interferer failures in the publication experiment. This supports the interpretation that high-density operation is primarily a many-interferer problem rather than a single-neighbor problem.

### 5.2 Resource separation is valuable despite reduced per-link bandwidth

At N=100 and G=0:

| Resources | Mean SINR (dB) | First-TX success | Expected goodput (Mbps) |
|---:|---:|---:|---:|
| 1 | -23.03 | 0.0128 | 0.359 |
| 2 | -16.20 | 0.0749 | 0.668 |
| 4 | -10.48 | 0.0775 | 0.572 |
| 8 | -5.47 | 0.2049 | 1.042 |

The non-monotonic goodput relationship between two and four resources is informative rather than an error: increased frequency isolation improves SINR, but additional partitioning also reduces per-link PRBs/TBS. Eight resources provide enough additional interference suppression in this evaluated configuration to overcome the bandwidth reduction and cross the 1 Mbps goodput target at N=100.

### 5.3 Directionality alone helps, but does not fully solve dense shared-resource operation

At N=100 with R=1, increasing the relative directional advantage from 0 to 9 dB changes mean SINR from -23.03 to -14.03 dB and goodput from 0.359 to 1.435 Mbps. However, first-transmission success reaches only 0.0494 at G=9, so this configuration still fails the explicit 0.10 success target. This illustrates why goodput and reliability must be considered jointly.

### 5.4 Resource separation and directionality are complementary

At N=100:

| R | G (dB) | Mean SINR (dB) | First-TX success | Expected goodput (Mbps) |
|---:|---:|---:|---:|---:|
| 1 | 0 | -23.03 | 0.0128 | 0.359 |
| 8 | 0 | -5.47 | 0.2049 | 1.042 |
| 2 | 6 | -10.20 | 0.1262 | 1.414 |
| 4 | 6 | -4.48 | 0.2193 | 1.608 |
| 8 | 6 | 0.53 | 0.5292 | 2.229 |
| 8 | 9 | 3.53 | 0.8050 | 3.493 |

Relative to the N=100 baseline, R=8,G=6 increases mean SINR by 23.55 dB, first-transmission success by roughly a factor of 41, and expected goodput by roughly a factor of 6.2. These ratios describe this evaluated model only.

Matched-seed statistics are generated automatically by `tools/summarize_paper_results.py` so that the final manuscript can report mean differences, 95% confidence intervals, Cohen's `dz`, and paired t-test p-values from the exact publication artifact.

### 5.5 Operating envelope

Under the explicit policy requiring first-transmission success >= 0.10 and expected goodput >= 1 Mbps, the maximum evaluated feasible swarm sizes are:

| R | G=0 dB | G=3 dB | G=6 dB | G=9 dB |
|---:|---:|---:|---:|---:|
| 1 | 10 | 10 | 20 | 50 |
| 2 | 50 | 75 | 100 | 100 |
| 4 | 50 | 75 | 100 | 100 |
| 8 | 100 | 100 | 100 | 100 |

The key result is not that “100 UAVs is supported” universally. Rather, within the evaluated geometry/channel/traffic abstraction, the feasible operating region shifts dramatically when interference is reduced before BLER mapping. Resource separation can be more effective than large directional gain alone, and moderate resource separation combined with moderate spatial selectivity can reach the same evaluated envelope boundary as more aggressive resource partitioning.

## 6. Discussion

### 6.1 Why retransmission is not the headline mechanism

The broader thesis campaign showed that when first-transmission TB BLER is already close to one at high density, idealized Chase-combining HARQ provides only limited recovery while adding latency. The paper therefore treats HARQ as supporting context rather than the central mitigation mechanism. Resource isolation and directional suppression improve the underlying SINR before retransmission is considered.

### 6.2 Bandwidth-interference trade-off

An important methodological point is that orthogonalization must be modeled with its bandwidth cost. If every link retained the full 133 PRBs while co-channel interference was simply removed, the resource benefit would be overstated. Exact PRB partitioning exposes a real trade-off: fewer co-channel interferers versus smaller TBS and narrower occupied bandwidth. The N=100 R=2 versus R=4 goodput result demonstrates why this accounting matters.

### 6.3 Implications for 6G-oriented aerial sidelink

The results motivate future aerial sidelink designs that jointly exploit resource coordination and spatial selectivity. A scheduler or distributed resource-selection mechanism could use local interference information to decide whether an additional orthogonal partition is worth its bandwidth cost. Directional arrays could then reduce residual co-channel interference. The present work does not implement those future algorithms; it provides the operating-region characterization needed to motivate and evaluate them.

## 7. Limitations

The following boundaries are essential to the interpretation:

- No measured multi-UAV RF interference, BLER, PDR, or end-to-end latency is claimed.
- The A2A propagation law is measurement-derived, but simulated geometries and RF realizations are not measurements.
- Numerical BLER curves are 5G-LENA link-level simulation data.
- The study is not a bit-accurate NR sidelink PHY implementation.
- Resource allocation is a project-specific conflict-graph abstraction, not normative Mode-1/Mode-2 behavior.
- The directionality variable is an experimental relative-gain/suppression sensitivity, not full MIMO/beam management.
- The model does not include full fast fading or a complete beam-tracking procedure.
- TB BLER from code-block BLER assumes independent code-block decoding events.
- The operating-envelope thresholds are engineering policy choices and sensitivity points, not 3GPP requirements.
- The largest evaluated N is not a universal swarm capacity limit.

## 8. Conclusion

The study shows that dense shared-resource UAV sidelink operation becomes severely interference-limited, with high-density failure behavior dominated by aggregate interference. Exact frequency-resource partitioning can recover substantial reliability even after accounting for the corresponding PRB/TBS reduction, while directional spatial selectivity provides additional complementary gain. Under the evaluated engineering policy, the feasible swarm-size envelope expands from N=10 in the unmitigated baseline to the N=100 boundary of the evaluated grid for several resource/directionality combinations. The central design implication is therefore not to rely on retransmission alone, but to reduce interference before decoding through coordinated resource reuse and spatial selectivity. Future work should validate these trends with standards-complete sidelink scheduling/beam management and, ultimately, multi-UAV RF measurements.

## References

[1] D. Mishra, A. Trotta, E. Traversi, M. Di Felice, and E. Natalizio, “Cooperative Cellular UAV-to-Everything (C-U2X) communication based on 5G sidelink for UAV swarms,” *Computer Communications*, vol. 192, pp. 173–184, 2022. DOI: `10.1016/j.comcom.2022.06.001`.

[2] W. J. Lau, J. M.-Y. Lim, C. Y. Chong, N. S. Ho, and T. W. M. Ooi, “General Outage Probability Model for UAV-to-UAV links in Multi-UAV Networks,” *Computer Networks*, vol. 229, 109752, 2023. DOI: `10.1016/j.comnet.2023.109752`.

[3] M. Varonen, “Using NR Sidelink for UAV Swarm Internal Communication,” Master's thesis, Aalto University, 2024. URN: `URN:NBN:fi:aalto-202403172777`.

[4] “Joint Trajectory Control, Frequency Allocation, and Routing for UAV Swarm Networks: A Multi-Agent Deep Reinforcement Learning Approach,” *IEEE Transactions on Mobile Computing*, vol. 23, no. 12, pp. 11989–12005, 2024. DOI: `10.1109/TMC.2024.3403890`.

[5] A. Giannakoulas et al., “Sidelink Communication for Unmanned Platforms' (UxU) Swarms in Challenging Scenarios,” 6th International Conference on Communications, Information, Electronic and Energy Systems (CIEES), 2025. DOI: `10.1109/CIEES66347.2025.11300255`.

[6] H. Zhang, H.-M. Chen, Q.-J. Wei, Z.-W. Wang, and Y.-H. Sun, “Optimized Synchronization Design for UAV Swarm Network Based on Sidelink,” *Drones*, vol. 10, no. 4, 304, 2026. DOI: `10.3390/drones10040304`.

[7] U. Erdemir et al., “Measurement-based Channel Characterization for A2A and A2G Wireless Drone Communication Systems,” IEEE VTC 2023-Spring, 2023. DOI: `10.1109/VTC2023-Spring57618.2023.10199853`.

[8] N. Patriciello et al., “An E2E simulator for 5G NR networks,” *Simulation Modelling Practice and Theory*, vol. 96, 101933, 2019. DOI: `10.1016/j.simpat.2019.101933`.

[9] 5G-LENA v5.0 software archive. DOI: `10.5281/zenodo.21165297`.

[10] 3GPP TR 38.901 V19.4.0; 3GPP TR 36.777; 3GPP TS 38.211/38.212/38.213/38.214 and TS 38.104, exact project-recorded versions.

## Reproducibility note

The first completed full publication artifact was produced by workflow `paper-operating-envelope`, run #1, at Git commit `8d28e57e97e2c16c03c4a45636a9e4083ce11c02`, artifact ID `9997612090`, digest `sha256:b43c9a9ce7c1f23774ccc4df04e1489ce852cf116c32ffd1cc20e9daf6dabe21`. A later performance-only BLER lookup optimization preserves the exact curve-selection semantics; the final evidence freeze should reference the newest successful publication artifact after manuscript-statistics integration.
