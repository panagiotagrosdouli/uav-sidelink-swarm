# 011 — Full experimental campaign audit

## Scope

Starting point: `main` commit `6cf44d77f6ae8037148a3e5d21ff68f9fe65be89`.

This audit applies the master experimental-program specification before the
canonical final campaign is frozen. It is an engineering/research log, not
thesis prose.

## Capability matrix

| Capability | Implemented at audit start | Tested | Source-backed | Validation state | Action in full-campaign branch |
|---|---:|---:|---:|---|---|
| Erdemir 3.5 GHz A2A fit | yes | yes | yes | measurement-derived model anchors | retain |
| FSPL reference | yes | yes | analytical | reference checks | retain |
| TR 38.901/36.777 equal-height UMi-AV | yes | yes | yes | restricted validity checked | retain; use only valid altitude range |
| Common co-channel SINR | yes | yes | mixed | reproducible | extend with resource IDs and interference decomposition |
| Density Monte Carlo | yes | CI smoke | mixed | reproducible | extend to N=75/100 and fixed-density family |
| Synthetic geometries | uniform only | partial | SYNTHETIC | missing | add grid/circle/clustered/leader-follower |
| Real AMOVFLY loader | yes | yes | MEASURED_DATASET | local-frame ambiguity | transform global GPS to common WGS-84 ENU |
| Resource allocation | random + greedy | yes | THIS_WORK | system abstraction | add weighted conflict-graph heuristic and fairness |
| Routing | min-hop + quality | yes | THIS_WORK | graph abstraction | add reliability/latency composition |
| Directional gain | scalar sensitivity | smoke | EXPERIMENTAL_SWEEP | not MIMO | split desired gain/suppression; optional ULA factor |
| NR MCS Table 1 | yes | yes | STANDARD | anchors checked | retain |
| 5G-LENA BLER | limited BG1 fixture | yes | LINK_LEVEL_SIMULATION | insufficient coverage | parse BG1+BG2; runtime-fetch pinned v5.0 full table |
| TBS | yes | yes | STANDARD | implemented | retain |
| LDPC BG/segmentation | yes | yes | STANDARD | implemented | retain |
| TBS-aware link adaptation | partial | partial | mixed | fixed-CBS limitation | select MCS using TBS→BG/CBS→BLER |
| HARQ | ideal Chase abstraction | yes | DERIVED | explicitly non-bit-accurate | sweep attempts/gap; no invented IR gain |
| Sidelink overhead | yes | yes | standard-constrained + configured | sensitivity only | retain |
| Traffic load | no | no | — | missing | add explicit Poisson slot-activity abstraction |
| Fairness | no | no | analytical metric | missing | add Jain index |
| Energy per delivered bit | no | no | DERIVED | missing | add Tx-energy-only abstraction |
| Shadow fading | model sigma helper exists | partial | STANDARD for UMi-AV | not in system engine | add explicit sigma input; use only sourced UMi-AV case |
| Fast fading | no | — | — | out of scope | retain explicit limitation |
| Statistical CI | experiment-specific | partial | analytical | inconsistent | add common Student-t/bootstrapped helpers |
| Final campaign manifest | general runner exists | yes | provenance framework | no canonical frozen campaign | add final-campaign manifest/config/results |
| Thesis-ready final figures | partial | smoke | derived | incomplete | generate stable final_campaign figure set |
| Failure analysis | no | no | DERIVED | missing | add per-link failure decomposition |
| Fixed-area vs fixed-density | no | no | SYNTHETIC | missing | add core scaling experiment |
| Legacy 5.9 GHz prototype | yes | old | experimental | conflicts with baseline | deprecate and redirect to common engine |

## Scientific blockers identified

1. **Full link-level coverage:** the repository cannot call its adaptive-MCS
   study broad while it carries only MCS 4/5/6 BG1/CBS4096 fixture curves.
2. **Measured mobility frame:** pairwise subtraction of AMOVFLY local coordinates
   is unsafe unless a common origin is verified.
3. **Metric consistency:** BLER/goodput/latency/fairness need one common evaluator
   before multi-dimensional comparisons.
4. **Scaling interpretation:** fixed-area and fixed-spatial-density experiments
   must be separated to avoid conflating swarm size with spatial density.

## Out-of-scope unless independently validated

- bit-accurate NR Sidelink PHY;
- normative Mode-2 scheduler;
- complete HARQ Incremental Redundancy history processing;
- full fast fading;
- complete MIMO/beam management;
- measured multi-UAV RF interference, PDR or E2E latency.

These remain limitations rather than being filled with synthetic claims.
