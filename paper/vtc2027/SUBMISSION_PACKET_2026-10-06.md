# VTC2027-Spring submission packet

Prepared: 2026-10-06

## Venue status

- Venue: IEEE VTC2027-Spring
- Location/dates: Hamburg, Germany, 20–23 June 2027
- Regular-paper deadline: **14 October 2026 — final extension**
- Standard paper length: **5 pages**
- Current topology-first PDF build: CI-verified at 5 pages
- Compiled workflow artifact: `VTC2027-Spring-UAV-Sidelink-Draft`
- Artifact ID: `11441102856`
- Artifact digest: `sha256:396a0c1b1458f5c9404c5a93542f0cf7849eb8f4271febc037f1a68ee53dcd7b`

## Recommended submission metadata

### Title

**Topology-Conditioned Interference and Resource-Isolation Trade-offs in 5G NR Sidelink UAV Swarms**

### Primary track

**Space, Non-terrestrial, Airborne, and Maritime Mobile Systems and Services**

Reason: the application domain and central contribution are aerial/UAV communications, with sidelink interference and resource-management analysis.

### Secondary track if the portal requests an alternative

**Radio Access Technology and Heterogeneous Networks**

Other defensible alternative: **IoT, M2M, Sensor Networks, and Ad-Hoc Networking, Cooperative Communication**.

### Keywords

- 5G NR sidelink
- UAV swarm
- topology
- interference
- resource isolation
- link adaptation
- operating region
- reproducibility

## Portal abstract

Direct NR sidelink is a candidate for infrastructure-independent UAV-swarm communication, but dense aerial line-of-sight conditions make scalability depend on more than swarm size alone. We present a measurement-grounded, NR-aware system-level study of communication topology, exact frequency-resource partitioning, and directional desired/interferer selectivity. A 100-seed campaign evaluates 5–100 UAVs, partitions a 133-PRB profile over 1/2/4/8 abstract orthogonal resources, and tests 0–9 dB relative desired/interferer advantage. Under the full-load sequential-disjoint baseline, N=100 yields -23.03 dB mean SINR, 0.0128 first-transmission success probability, and 0.359 Mbps expected PHY goodput. Yet greedy short-link pairing at the same N,R=1,G=0 reduces mean desired-link length from 517 m to 84 m and raises success probability to 0.4766 and goodput to 15.116 Mbps. Resource partitioning and spatial selectivity expand the evaluated reliability–goodput region, but partitioning exhibits a non-monotonic interference/bandwidth trade-off. The results therefore support topology-conditioned operating regions rather than a universal density-only swarm-capacity claim.

## One-sentence novelty statement

This work provides a controlled NR-aware characterization of how communication topology changes UAV-swarm interference scaling and when resource isolation remains beneficial after its reduced PRB/TBS budget is propagated through link adaptation and BLER mapping.

## Three contributions for reviewer/portal text

1. A measurement-grounded, NR-aware system-level evaluation using a published 3.5 GHz A2A path-loss fit, standards-derived transport-block mechanics, and sourced 5G-LENA v5.0 BLER evidence.
2. A matched-seed demonstration that communication topology is a first-order scaling variable, preventing density-only interpretations of the severe long-link baseline.
3. An explicit resource-isolation and spatial-selectivity operating-region study that charges orthogonalization for its PRB/TBS cost and includes allocator, fixed-MCS, and noise-bandwidth robustness controls.

## Claims that must not appear in portal text

- Do not state that 100 UAVs are universally supported.
- Do not call the conflict-graph allocator normative Mode 1/Mode 2.
- Do not call G a measured beamforming gain.
- Do not describe expected PHY goodput as application throughput.
- Do not describe 5G-LENA BLER curves as UAV measurements or 3GPP-standard BLER tables.
- Do not claim topology control itself is novel.

## Human-only fields to confirm before upload

- [ ] Final author list and order
- [ ] Corresponding-author email
- [ ] Exact university/department affiliation wording
- [ ] Supervisor/co-author approval
- [ ] Submission-account author metadata
- [ ] Track selection in the portal
- [ ] Any conflict-of-interest declarations requested by the portal

Do not invent or auto-fill any of these fields.

## CI evidence for this revision

All workflows associated with the topology-first revision completed successfully:

- `vtc2027-paper` run #21 — success
  - figures generated
  - citation-key integrity passed
  - IEEE LaTeX compiled
  - no undefined citations/references
  - five-page limit passed
  - no overfull boxes
  - compiled submission artifact uploaded
- `paper-reviewer-validation` run #20 — success
- `scientific-ci` run #397 — success

## Final upload rule

Upload only the CI-built PDF corresponding to the final approved source revision. If author metadata, acknowledgments, references, figures, or prose are edited after the verified build, rebuild and re-run the paper QA before submission.
