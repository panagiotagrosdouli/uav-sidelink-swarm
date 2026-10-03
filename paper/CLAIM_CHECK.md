# Manuscript claim guardrails

Use this file during manuscript editing so wording remains aligned with the current canonical thesis evidence.

| Topic | Allowed wording | Do not claim |
|---|---|---|
| A2A channel | measurement-derived fitted large-scale path-loss model | raw measured swarm RF at simulated distances |
| 5G-LENA BLER | `LINK_LEVEL_SIMULATION` curves from official v5.0 source | 3GPP-standard BLER curves or UAV measurements |
| Resource allocation | `THIS_WORK` conflict-graph system abstraction | normative NR Sidelink Mode 1/2 |
| Directionality | `EXPERIMENTAL_SWEEP` relative desired/interferer advantage | full MIMO, beam tracking, or measured antenna gain |
| Reliability | first-transmission success derived from modeled TB BLER | measured PDR |
| Goodput | expected PHY goodput under the evaluated model | end-to-end application throughput |
| Envelope | largest evaluated N satisfying explicit policy thresholds | universal maximum swarm capacity |
| Statistics | matched deterministic-seed system-level comparisons with t/bootstrap CIs and non-parametric sensitivity | independent field trials |
| Pairing | primary geometry-independent disjoint-peer control regime; nearest-neighbour matched-seed sensitivity | representative of every UAV swarm traffic pattern |
| Link adaptation | `THIS_WORK` TBS-aware model-based MCS selection | normative 3GPP AMC or perfect real-world CSI implementation |
| Occupied bandwidth | allocated PRBs × 12 subcarriers × SCS for thermal-noise accounting | treating every partition as full 50 MHz payload bandwidth |
| Mobility | measured telemetry used for trajectory/mobility evidence | measured RF performance inferred from telemetry |

## Current canonical evidence

The authoritative readiness state is `docs/FINAL_READINESS.md` and the successful final-thesis campaign on `main`.

- Canonical scientific commit: `fcae537ef0846b94c0c73ce306e15c406ab542f7`
- Final-thesis-campaign: run #5
- Registered experiments: 18/18 successful
- Canonical figures: 17/17 present
- Scientific audit failures: 0
- Main full-campaign studies: 100 deterministic seeds

Historical publication freezes remain in `docs/experiments/` for provenance and must not override the current readiness gate.

## Publication-specific hardened evidence

For the submission paper, the authoritative numerical source is the reviewer-hardened `paper-operating-envelope` workflow and the evidence record `docs/experiments/013_reviewer_hardened_publication_evidence.md`.

Mandatory interpretation boundaries:

- the primary operating envelope is conditioned on geometry-independent disjoint peer pairing and the weighted conflict-graph allocator;
- random-allocation results must be used when attributing gains specifically to frequency partitioning versus allocation policy;
- nearest-neighbour pairing results must be reported as evidence that communication locality materially changes absolute performance;
- p-values are secondary; matched effect magnitudes and confidence intervals are primary;
- older publication run #3 is historical provenance and must not override the hardened publication evidence.
