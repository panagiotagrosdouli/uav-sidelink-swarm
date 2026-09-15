# Submission readiness audit

This checklist is tied to the current canonical thesis evidence and prevents manuscript claims from drifting away from the successful final campaign.

## Canonical evidence

- Canonical scientific commit: `fcae537ef0846b94c0c73ce306e15c406ab542f7`
- Final-thesis-campaign: run #5
- Workflow conclusion: `success`
- Registered experiments: `18/18 successful`
- Canonical figures: `17/17 present`
- Scientific audit checks: `304`
- Scientific audit failures: `0`
- Missing external/optional evidence: `0`
- Main full-campaign Monte-Carlo studies: `100 deterministic seeds`

Historical publication runs remain preserved for provenance but are not authoritative for current readiness.

## Headline evidence

At `N=100`, the canonical publication evidence reports the baseline `R=1, G=0 dB` and mitigated `R=8, G=6 dB` cases as:

- mean SINR: `-23.03 -> 0.53 dB`;
- mean first-transmission success: `0.013 -> 0.529`;
- mean expected PHY goodput: `0.359 -> 2.229 Mbps`.

The matched-seed comparison over 100 deterministic seeds gives:

- first-transmission success difference: `+0.516358`, 95% CI `[0.505829, 0.526887]`, Cohen `dz=9.6122`, paired-t `p=1.4474e-99`;
- expected PHY goodput difference: `+1.870079 Mbps`, 95% CI `[1.728555, 2.011603]`, Cohen `dz=2.5899`, paired-t `p=6.9415e-46`.

These are `DERIVED_SYSTEM_LEVEL_METRIC_MATCHED_SEED_COMPARISON` results, not measurements.

## Claim-preserving requirements

1. Describe the A2A propagation law as a fitted measurement-derived large-scale model; simulated RF values are model-derived.
2. Describe 5G-LENA BLER as `LINK_LEVEL_SIMULATION` evidence, not 3GPP-standard BLER curves or UAV measurements.
3. Describe the conflict-graph allocator as a `THIS_WORK` system-level abstraction, not normative NR Sidelink Mode 1/2 scheduling.
4. Describe `G` as an experimental relative desired/interferer sensitivity (`+G/2` desired and `-G/2` interference), not measured beamforming gain or full MIMO.
5. Describe reliability as first-transmission success derived from modeled TB BLER, not measured PDR.
6. Describe goodput as expected PHY goodput under the evaluated model, not end-to-end application throughput.
7. Describe the operating envelope as the largest **evaluated** swarm size satisfying explicit policy thresholds, not a universal capacity limit.
8. Do not introduce unsupported claims about measured swarm RF interference, measured PDR/BLER, end-to-end latency, full fast fading, or beam tracking.
9. Treat AMOVFLY telemetry as mobility/trajectory evidence unless user-supplied raw data support an additional analysis.

## Editorial gate

Before venue formatting:

- ensure all numerical claims match the current final campaign;
- include the matched-seed confidence intervals and effect sizes in Results;
- separate implemented mechanisms from design implications in Discussion;
- keep limitations adjacent to the strongest system-level claims;
- verify references against the project's literature evidence before submission;
- only then apply venue-specific page/template constraints.

## Final gate

The scientific implementation and reproducibility package is ready for thesis/research handoff. Further scientific changes that affect results must create a new campaign commit and evidence record rather than silently modifying the frozen state.