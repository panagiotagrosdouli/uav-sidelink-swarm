# Pre-submission reviewer audit — 2026-10-06

## Overall assessment

**Current scientific status:** conference-submittable after editorial compression.

**Best framing:** topology-conditioned operating-region characterization, not a claim of universal density-driven sidelink collapse and not a standards-complete NR sidelink implementation.

## Strongest evidence

1. **Topology sensitivity is first-order.** At N=100,R=1,G=0, nearest-neighbour pairing changes mean desired distance 517.20 -> 84.05 m, mean SINR -23.03 -> -1.75 dB, first-TX success 0.0128 -> 0.4766, and expected goodput 0.359 -> 15.116 Mbps.
2. **Resource isolation has a non-trivial bandwidth cost.** At N=100,G=0, R=2 -> R=4 improves mean SINR (-16.20 -> -10.48 dB) but reduces expected goodput (0.668 -> 0.572 Mbps).
3. **Joint mitigation produces a large matched-seed effect.** At N=100, R=8,G=6 versus R=1,G=0 yields +0.516358 first-TX success and +1.870079 Mbps expected goodput, with reported confidence intervals and large paired effect sizes.
4. **Reviewer-facing sensitivity checks exist.** Pairing, allocator, link adaptation, and noise-bandwidth conventions have been explicitly tested over 100 seeds.

## Major reviewer risks and controls

### Risk 1 — Baseline topology may look artificially harsh
**Control:** make topology sensitivity a main result, not an appendix-style robustness result. Never state that density alone causes the reported collapse.

### Risk 2 — Conflict-graph allocation may be mistaken for NR Mode 2
**Control:** label it repeatedly as a THIS_WORK geometry-aware system abstraction and include seeded random allocation as the no-coordination control.

### Risk 3 — Directionality parameter may be over-interpreted
**Control:** describe G only as an experimental desired/interferer relative advantage. Do not call it measured beamforming gain or full MIMO.

### Risk 4 — Link adaptation is optimistic
**Control:** state that expected-goodput-maximizing MCS assumes idealized instantaneous modeled SINR and show the fixed-MCS-4 sensitivity.

### Risk 5 — "NR sidelink" could imply standards completeness
**Control:** use "NR-aware system-level" in the abstract and methodology; list the specific standards-based mechanics and the exact missing Mode-1/Mode-2/PHY elements.

### Risk 6 — Novelty overlap with recent topology-control literature
**Control:** cite Bai et al. (IEEE WCL 2026) explicitly and state that topology control itself is not the novelty. The novelty claim is the controlled NR-aware operating-region characterization with explicit resource bandwidth cost and reliability/goodput mapping.

## Recommended reviewer-facing claims

Supported:

- swarm-size effects are strongly conditioned by communication topology;
- exact resource isolation trades interference reduction against PRB/TBS loss;
- spatial selectivity and resource isolation are complementary in the evaluated model;
- geometry-aware allocation outperforms seeded random reuse in the tested cases;
- the reported operating envelope is an evaluated policy region, not a capacity theorem.

Do not claim:

- universal maximum supported UAV count;
- measured swarm RF/PDR/BLER/latency;
- normative NR Mode-1/Mode-2 scheduling;
- full MIMO/beam tracking;
- topology control as a previously unstudied topic.

## Editorial priority before upload

1. Convert to IEEE conference template.
2. Keep 3 main figures and at most 2 compact tables.
3. Put topology result on page 3 before the resource envelope.
4. Verify all DOI/reference metadata in the final PDF.
5. Run a final numerical claim audit against the frozen evidence artifact.
6. Obtain supervisor/co-author approval before submission.

## Internal readiness verdict

**Proceed to VTC2027-Spring preparation.** No new scientific feature is required for a defensible conference submission; effort should now go to compression, positioning, figures, and reference verification.