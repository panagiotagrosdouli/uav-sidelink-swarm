# UAV Sidelink Swarm

Research-oriented Python system-level simulation project for **5G NR Sidelink communication inside UAV swarms**.

## Thesis goal

Study how UAV swarm density and mobility affect UAV-to-UAV link quality, interference, reliability, latency, capacity/goodput and network connectivity, then evaluate controlled improvements from resource allocation, routing, link adaptation, HARQ and directional antenna gains.

The scientific pipeline is:

`SOURCE -> MODEL -> IMPLEMENTATION -> VALIDATION -> EXPERIMENT -> RESULT -> INTERPRETATION -> LIMITATIONS`

---

# Canonical thesis results

The results below are from **final-thesis-campaign run #5** on canonical Git commit:

`fcae537ef0846b94c0c73ce306e15c406ab542f7`

Run #5 completed successfully with:

- **18/18 registered experiments successful**
- **17/17 canonical figures present**
- **304 scientific audit checks**
- **0 scientific audit failures**
- **0 missing external/optional evidence**
- 100 deterministic Monte-Carlo seeds for the main full-campaign studies
- artifact digest: `sha256:a0dbfbeaa24a371502a584ecf137c65df8a1afd7af23f038ee40ad3cede33e47`

All numerical RF/network results below are simulation/model-derived unless explicitly identified as measured telemetry. They are **not field measurements of swarm RF performance**.

## 1. Swarm density strongly degrades the shared-channel link

In the canonical NR link-performance study, increasing the swarm from 5 to 100 UAVs substantially increases aggregate co-channel interference.

| UAVs | Mean SINR (dB) | Mean BLER | First-TX success | Expected PHY goodput (Mbps) |
|---:|---:|---:|---:|---:|
| 5 | -0.49 | 0.651 | 0.349 | 14.106 |
| 10 | -8.74 | 0.932 | 0.068 | 2.891 |
| 20 | -13.69 | 0.971 | 0.029 | 1.177 |
| 30 | -16.06 | 0.977 | 0.023 | 0.910 |
| 50 | -19.01 | 0.987 | 0.013 | 0.523 |
| 75 | -21.33 | 0.991 | 0.009 | 0.356 |
| 100 | -23.03 | 0.994 | 0.006 | 0.248 |

**Interpretation:** under the evaluated full-activity shared-resource configuration, swarm scaling is interference-limited. Link adaptation alone cannot compensate for the interference growth at high density.

Canonical figures: `fig02_sinr_density`, `fig03_sinr_cdf`, `fig04_bler_density`, `fig05_goodput_density`.

## 2. Scaling experiment

For the separate scaling geometry/activity experiment, mean SINR changed from approximately **7.52 dB at N=5** to **-1.75 dB at N=100** in the fixed-area family. The final N=100 95% confidence interval was **[-1.89, -1.61] dB**.

The fixed-density family produced approximately **7.53 dB at N=5** and **-1.75 dB at N=100**, with the same final 95% confidence interval in this evaluated nearest-neighbour/scaling abstraction.

This experiment is a different scenario family from the canonical full-activity NR link-performance table above and should not be numerically conflated with it.

Canonical figure: `fig13_scaling`.

## 3. Resource allocation reduces interference

At **N=50**, increasing the number of abstract orthogonal resources substantially improved the derived PHY performance.

Best evaluated point:

- allocator: `greedy`
- resources: `8`
- mean SINR: **-0.62 dB**
- first-TX success probability: **0.289**
- mean expected PHY goodput: **1.471 Mbps**
- Jain goodput fairness: **0.291**

For comparison, the single-resource case produced approximately **-18.97 dB SINR**, **0.011 first-TX success**, and **0.455 Mbps expected PHY goodput**.

The `random`, `greedy` and graph-conflict algorithms are **system-level research abstractions (`THIS_WORK`)**, not normative 3GPP Mode-1/Mode-2 schedulers.

Canonical figure: `fig07_resource_allocation`.

## 4. Directionality / beamforming sensitivity can compensate for interference

At the N=30 sensitivity point, the shared-channel baseline was:

- mean SINR: **-16.06 dB**
- first-TX success: **0.0225**
- expected PHY goodput: **0.910 Mbps**

For the experimental `combined` desired-gain + interference-suppression sensitivity:

| Directionality parameter | Mean SINR (dB) | First-TX success | Expected goodput (Mbps) |
|---:|---:|---:|---:|
| 0 dB | -16.06 | 0.023 | 0.910 |
| 3 dB | -10.06 | 0.056 | 2.314 |
| 6 dB | -4.06 | 0.183 | 7.439 |
| 9 dB | 1.94 | 0.481 | 19.771 |

The gain values are an **experimental sensitivity sweep**, not measured antenna gains and not a full MIMO/beam-management implementation. The repository also contains a normalized ULA array-factor study as a physical directionality abstraction.

Canonical figures: `fig09_beamforming`, `fig16_ula`.

## 5. HARQ helps only when the underlying link is recoverable

At **N=100**, the first-transmission TB BLER is approximately **0.995** in the evaluated shared-channel scenario. With the ideal Chase-Combining abstraction and up to four attempts, final success remains only about **0.0101**.

Increasing the feedback/retransmission gap increases latency and reduces delivered goodput:

| Feedback gap (slots) | Mean latency (ms) | Delivered goodput (Mbps) |
|---:|---:|---:|
| 1 | 3.48 | 0.145 |
| 2 | 4.97 | 0.136 |
| 4 | 7.95 | 0.127 |
| 8 | 13.90 | 0.120 |

**Interpretation:** retransmissions cannot by themselves solve a severely interference-limited link. Resource separation and/or directionality must improve the underlying SINR first.

Canonical figures: `fig06_latency_density`, `fig10_harq`.

## 6. Cross-layer ablation

After removing unsupported graph-partition TBS/BLER combinations from the bundled-fixture ablation, the best evaluated fixture-supported mechanism at **N=100** was:

`adaptive_harq4_directional6_shared`

with:

- mean success probability: **0.0337**
- modeled goodput: **0.387 Mbps**
- mean latency: **4.91 ms**

For comparison:

- adaptive MCS shared: **0.116 Mbps**
- adaptive HARQ4 shared: **0.136 Mbps**
- adaptive directionality6 shared: **0.316 Mbps**
- fixed MCS4 shared: **0.088 Mbps**

This supports the cross-layer conclusion that no single mechanism completely removes the high-density interference problem, while directionality combined with HARQ gives the strongest evaluated improvement in the fixture-supported ablation.

Canonical figure: `fig12_ablation`.

## 7. Failure mechanism changes with density

The failure diagnostic uses an explicit first-transmission success target of 0.5 as an **experimental policy threshold**.

At N=10, failed links were more often classified as dominated by a strongest interferer (**59.8%**) than aggregate interference (**33.6%**).

At N=100, aggregate interference became dominant (**72.16%**) while the dominant-interferer category fell to **27.34%**.

**Interpretation:** as swarm density increases, the interference problem transitions toward a many-interferer aggregate regime, strengthening the motivation for resource coordination and spatial interference suppression.

Canonical figure: `fig15_failures`.

## 8. Multi-hop routing becomes available as topology density increases

Routing is evaluated on an isolated-link graph abstraction with:

- farthest source/destination pair per realization
- minimum modeled link-success threshold: `0.5`
- maximum routing hop distance: `350 m`
- the 350 m limit is an **EXPERIMENTAL_CONFIGURATION**, not a 3GPP range requirement

Observed route connectivity probability:

| UAVs | Route connectivity | Mean min-hop path length |
|---:|---:|---:|
| 10 | 0.17 | 4.41 hops |
| 20 | 0.72 | 4.83 hops |
| 30 | 0.95 | 4.77 hops |
| 50 | 1.00 | 4.56 hops |
| 75 | 1.00 | 4.59 hops |
| 100 | 1.00 | 4.54 hops |

The routing study is intentionally separated from the simultaneous shared-channel interference experiment. Its route probabilities therefore describe graph/path feasibility under the isolated-link model, not measured or end-to-end swarm PDR.

Canonical figure: `fig08_routing`.

## 9. Real AMOVFLY mobility evidence

The canonical public AMOVFLY pair produced:

- **1831 synchronized telemetry samples**
- **366.0 s** overlap
- minimum horizontal separation: **2.06 m**
- mean horizontal separation: **43.87 m**
- median horizontal separation: **40.64 m**
- maximum horizontal separation: **127.75 m**
- frame: `COMMON_ENU_WGS84_HORIZONTAL_ONLY`
- distance dimension: `2D_HORIZONTAL`

The UAV trajectories are based on **measured telemetry (`MEASURED_DATASET`)**. Synchronization, coordinate conversion and separation are **derived from the measured dataset**. The canonical mobility analysis deliberately generates **no RF/SINR/BLER/goodput claim** from this pair.

Canonical figure: `fig11_real_mobility`.

## 10. Traffic-load experiment

The explicit Poisson/slotted traffic abstraction shows severe queueing under the evaluated shared-channel conditions. For example, at N=50 the mean delivery ratio decreases from approximately **0.0476 at 50 packets/s/link** to **0.0098 at 1500 packets/s/link**, while utilization approaches one.

These values are `DERIVED_SYSTEM_LEVEL_METRIC` outputs of the experimental traffic/service abstraction. They are not measured application-layer UAV latency/PDR and should be interpreted mainly as evidence of saturation under poor shared-channel reliability.

Canonical figure: `fig17_traffic`.

---

# Main thesis conclusion from the campaign

The evaluated system-level evidence supports four main conclusions:

1. **Density is the dominant stressor in an uncoordinated/shared-resource swarm.** Aggregate co-channel interference causes strong SINR, reliability and goodput degradation as N increases.
2. **Resource separation is highly effective** because it directly reduces the number of simultaneous co-channel interferers.
3. **Directionality has the largest compensation potential among the evaluated PHY-side sensitivity mechanisms**, especially when desired gain and interference suppression act together; however, this is a sensitivity study rather than a complete MIMO implementation.
4. **HARQ and routing are complementary rather than substitutes for interference management.** HARQ cannot rescue links whose first-transmission BLER is already near one, while routing benefits from denser graph connectivity but is evaluated in an isolated-link topology abstraction.

The results therefore motivate a 6G-oriented UAV-swarm design combining **resource coordination + spatial selectivity/directionality + adaptive link control + topology-aware routing**, rather than relying on one mechanism alone.

---

## Scientific data policy

Every important quantity is classified as one of:

- `MEASURED` / `MEASURED_DATASET`
- `STANDARD`
- `LITERATURE`
- `LINK_LEVEL_SIMULATION`
- `DERIVED`
- `DERIVED_FROM_LINK_LEVEL_SIMULATION`
- `DERIVED_SYSTEM_LEVEL_METRIC`
- `EXPERIMENTAL_SWEEP`
- `EXPERIMENTAL_ASSUMPTION`
- `EXPERIMENTAL_CONFIGURATION`
- `SYNTHETIC`
- `THIS_WORK`

Synthetic simulation values are never presented as real measurements.

## Implemented research layers

### Published measurement-derived A2A propagation

Primary peer-reviewed source: U. Erdemir et al., **“Measurement-based Channel Characterization for A2A and A2G Wireless Drone Communication Systems,”** IEEE VTC 2023-Spring, DOI `10.1109/VTC2023-Spring57618.2023.10199853`.

The repository reproduces the reported A2A large-scale fit at 3.5 GHz using `eta=2.166` and `PL0=34.650 dB`. Values generated from this fit are measurement-derived, not raw RF samples.

### 3GPP Release-19 aerial-to-aerial large-scale channel

A deliberately limited and auditable equal-height UMi-AV A2A implementation is included from 3GPP TR 38.901 V19.4.0 Case 9 and the referenced TR 36.777 aerial-UE large-scale models. This is not a full fast-fading implementation.

### Standards-based MCS, TBS, LDPC and sourced BLER

NR MCS Table 1, TBS and LDPC mechanics are implemented from the recorded 3GPP Release-19 specifications. Numerical SINR-to-BLER curves are sourced from verified 5G-LENA link-level simulation data where available. These curves are not UAV field measurements and are not called 3GPP-standard BLER curves.

### Reproducible thesis pipeline

Run the full registered suite with:

```bash
python -m tools.run_thesis_pipeline
```

Validate only the registry/manifest with:

```bash
python -m tools.run_thesis_pipeline --dry-run
```

Validation:

```bash
pip install -r requirements.txt
python -m pytest -q
```

The canonical GitHub Actions workflow additionally runs the public AMOVFLY pair, finalizes the evidence bundle and executes the scientific audit.

## Canonical evidence locations

Key generated outputs in a completed full campaign include:

- `results/final_campaign/manifest.json`
- `results/final_campaign/audit_summary.json`
- `results/final_campaign/scientific_audit.csv`
- `results/final_campaign/key_findings.md`
- `results/final_campaign/parameter_provenance.csv`
- `results/final_campaign/scenario_definitions.csv`
- `results/final_campaign/*_summary.csv`
- `figures/final_campaign/fig01...fig17`

## Important limitations

The repository does **not** claim to implement:

- a bit-accurate NR Sidelink PHY;
- measured swarm RF interference, PDR or end-to-end latency;
- a normative Mode-1/Mode-2 scheduler;
- exact standards-complete HARQ IR/CC history processing;
- full 3GPP fast fading;
- full MIMO/beam management;
- a measured RF campaign derived from AMOVFLY telemetry.

Where sourced BLER curves are available, reliability is derived from BLER rather than a fixed SINR-success threshold. TBS, LDPC and MCS mechanics can be standards-based while final goodput, latency, fairness, routing and traffic metrics remain derived system-level outputs.

## Core references

- U. Erdemir et al., IEEE VTC 2023-Spring, DOI `10.1109/VTC2023-Spring57618.2023.10199853`.
- N. Patriciello et al., *Simulation Modelling Practice and Theory* 96 (2019), DOI `10.1016/j.simpat.2019.101933`.
- 5G-LENA v5.0 software archive, DOI `10.5281/zenodo.21165297`.
- 3GPP TR 38.901 V19.4.0 and TR 36.777.
- 3GPP TS 38.211 / 38.212 / 38.213 / 38.214 and TS 38.104, exact versions recorded in project documentation.

Detailed provenance is maintained under `references/` and experiment notes under `docs/experiments/`.
