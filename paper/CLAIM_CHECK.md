# Manuscript claim guardrails

Use this file during the submission edit so wording remains aligned with the frozen publication artifact.

| Topic | Allowed wording | Do not claim |
|---|---|---|
| A2A channel | measurement-derived fitted large-scale path-loss model | raw measured swarm RF at simulated distances |
| 5G-LENA BLER | `LINK_LEVEL_SIMULATION` curves from official v5.0 source | 3GPP-standard BLER curves or UAV measurements |
| Resource allocation | `THIS_WORK` conflict-graph system abstraction | normative NR Sidelink Mode 1/2 |
| Directionality | `EXPERIMENTAL_SWEEP` relative desired/interferer advantage | full MIMO, beam tracking, or measured antenna gain |
| Reliability | first-transmission success derived from modeled TB BLER | measured PDR |
| Goodput | expected PHY goodput under the evaluated model | end-to-end application throughput |
| Envelope | largest evaluated N satisfying explicit policy thresholds | universal maximum swarm capacity |
| Statistics | matched deterministic-seed system-level comparisons | independent field trials |

Canonical scientific evidence is frozen in `docs/experiments/012_publication_evidence.md`.