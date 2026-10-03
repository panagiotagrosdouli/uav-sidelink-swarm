# VTC2027-Spring — 5-page reviewer-hardened outline

Target contribution: **measurement-grounded, NR-aware characterization of a conditional interference operating envelope for dense UAV sidelink under exact frequency-resource partitioning, allocation-policy sensitivity, communication-locality sensitivity, and directional spatial selectivity.**

## Page 1 — Abstract + Introduction

Keep the abstract compact. Establish:

- NR sidelink relevance to infrastructure-independent UAV coordination;
- dense aerial LOS strengthens desired and interfering links;
- frequency isolation trades interference against PRB/TBS bandwidth;
- absolute performance also depends on peer-selection geometry.

End with exactly three contributions:

1. measurement-grounded / NR-aware system evaluation;
2. controlled density-dependent interference characterization;
3. exact-resource operating envelope with matched allocator/pairing robustness checks.

Do not claim universal swarm capacity.

## Page 2 — Related Work + System Model

Related work should concentrate on the closest UAV-sidelink, U2U outage/interference, and joint resource/routing studies.

Include a compact parameter table with:

- 3.5 GHz carrier;
- nominal 50 MHz / 30 kHz / 133 PRBs;
- exact occupied-noise bandwidth = allocated PRBs × 12 × SCS;
- 30 dBm Tx power;
- 7 dB receiver NF;
- 1000 m × 1000 m area;
- 100 m equal altitude;
- activity probability 1;
- primary geometry-independent disjoint pairing;
- primary weighted conflict-graph allocator;
- 100 matched deterministic seeds.

State that the primary pairing is deliberately geometry-independent so desired-link distance does not automatically shrink with N.

## Page 3 — NR-aware methodology + baseline density result

Explain:

- measurement-derived A2A large-scale path loss;
- exact 133-PRB partitioning;
- TBS/LDPC/CBS recomputation;
- sourced official 5G-LENA v5.0 Table-1 BLER curves;
- THIS_WORK TBS-aware link adaptation;
- G as an experimental desired/interferer relative advantage;
- paired Student-t and deterministic bootstrap CIs, Cohen dz, Wilcoxon sensitivity.

Main result: density-driven aggregate interference in the controlled peer regime.

## Page 4 — Operating envelope + allocator sensitivity

Show the primary N/R/G envelope, but explicitly label it as conditional on the primary pairing/allocator.

Immediately include random-vs-conflict-graph evidence. At N=100,G=0,R=8:

- random allocation: success 0.1463, goodput 0.815 Mbps;
- conflict graph: success 0.2049, goodput 1.042 Mbps.

This prevents the paper from attributing all R>1 gain to partitioning alone.

## Page 5 — Pairing sensitivity + Discussion + Limitations + Conclusion

Pairing is the strongest boundary condition. At N=100,R=1,G=0:

- geometry-independent pairing: mean desired distance 517.2 m, success 0.0128, goodput 0.359 Mbps;
- nearest-neighbour pairing: mean desired distance 84.0 m, success 0.4766, goodput 15.12 Mbps.

Interpretation: local peer selection can compensate for much of the density penalty. The main envelope therefore characterizes a controlled non-local-peer regime, not every swarm topology.

Close with limitations:

- no measured swarm RF/PDR/latency;
- no bit-accurate PHY/MAC;
- no normative Mode 1/2 allocator;
- no full fast fading;
- G is not measured beamforming;
- MCS selection is model-based THIS_WORK adaptation;
- policy thresholds are not 3GPP requirements.

## Figure budget

Preferred:

1. baseline vs mitigated density curve;
2. operating envelope or compact heatmap;
3. combined robustness figure for allocator and pairing effects.

Avoid routing, traffic, AMOVFLY and detailed HARQ figures in the main five-page paper.

## Final gate

The numerical source of truth is `MANUSCRIPT_SUBMISSION.md` plus `docs/experiments/013_reviewer_hardened_publication_evidence.md`. Historical publication freezes remain provenance only.
