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
| Statistics | matched deterministic-seed system-level comparisons; normal and paired-bootstrap CIs | independent field trials |
| Pairing / topology | baseline collapse is conditional on sequential-disjoint long-link topology; nearest-neighbour pairing materially improves the regime | density alone universally causes the reported collapse |
| Link adaptation | THIS_WORK expected-goodput-maximizing MCS; fixed-MCS robustness baseline | normative 3GPP AMC |
| Noise bandwidth | frozen run uses nominal-channel PRB-share convention; robustness uses exact PRB occupied bandwidth | claim that both conventions are numerically identical |
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
## Reviewer-hardening evidence rule

The `paper_robustness` experiment is supplementary sensitivity evidence and must not silently replace the frozen `paper-operating-envelope` values. Any robustness result cited in a manuscript revision must include its committed workflow/artifact provenance and identify the changed modeling dimension (pairing, allocator, link adaptation, or noise-bandwidth accounting).

## Topology-sensitive headline guardrail

The completed robustness campaign shows that pairing is a first-order variable. At N=100,R=1,G=0, nearest-neighbour pairing changes mean desired-link distance from ~517 m to ~84 m and first-TX success from 0.0128 to 0.4766. Therefore all density-collapse wording must explicitly identify the baseline topology or otherwise state topology dependence.
