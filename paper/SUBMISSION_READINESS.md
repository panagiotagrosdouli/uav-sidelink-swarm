# Submission readiness audit

This checklist is tied to the canonical publication evidence frozen in `docs/experiments/012_publication_evidence.md` and is intended to prevent manuscript claims from drifting away from the successful artifact.

## Canonical evidence

- Scientific SHA: `9fb112307270d9d39408e704f285ea91d20a735b`
- Workflow: `paper-operating-envelope`, run #3, ID `34085307799`
- Artifact ID: `10005074790`
- Artifact digest: `sha256:4a996afe9dffa7984a5a0cfa6276a6f727228cd1ee2cbbd6e7f1634e8c149137`
- 100 matched seeds per scenario
- 11,200 per-seed realizations
- 112 scenario summaries
- 84 matched-seed comparisons
- 16 operating-envelope points
- 0 missing values in audited publication tables
- BLER mode: `FULL_5GLENA_V5_LOCAL`

## Headline result that may be quoted

At `N=100`, comparing the mitigated `R=8, G=6 dB` configuration with the `R=1, G=0 dB` baseline:

- mean SINR: `-23.03 -> 0.53 dB`;
- mean first-TX success: `0.013 -> 0.529`;
- mean expected PHY goodput: `0.359 -> 2.229 Mbps`.

Matched-seed effect sizes:

- first-TX success difference: `+0.516358`, 95% CI `[0.505829, 0.526887]`, Cohen `dz=9.6122`, paired-t `p=1.4474e-99`, `n=100`;
- expected PHY goodput difference: `+1.870079 Mbps`, 95% CI `[1.728555, 2.011603]`, Cohen `dz=2.5899`, paired-t `p=6.9415e-46`, `n=100`.

These are `DERIVED_SYSTEM_LEVEL_METRIC_MATCHED_SEED_COMPARISON` results, not measurements.

## Required manuscript edits before submission

1. Replace the stale final `Reproducibility note` in `paper/MANUSCRIPT.md`, which still points to publication run #1, with the canonical run #3 identifiers above.
2. Replace the placeholder sentence in Section 5.4 about statistics being generated later with the frozen matched-seed effect sizes above.
3. Keep the operating-envelope wording as **largest evaluated feasible swarm size**. Never state or imply a universal capacity limit.
4. Keep `G` explicitly defined as a relative desired/interferer sensitivity abstraction (`+G/2` desired, `-G/2` interference), not measured beamforming gain or full MIMO.
5. Keep 5G-LENA BLER curves classified as `LINK_LEVEL_SIMULATION`; do not call them 3GPP BLER curves or UAV measurements.
6. Keep the Erdemir A2A coefficients described as fitted/measurement-derived parameters; arbitrary-distance RF values are model-derived.
7. Do not call the conflict-graph resource allocator normative NR Sidelink Mode 1/2.
8. Do not introduce measured swarm PDR, measured RF interference, end-to-end latency, fast-fading, or beam-tracking claims that are absent from the canonical evidence.

## Editorial pass

Before venue formatting, the manuscript should receive one claim-preserving editorial pass focused on:

- shortening the abstract while retaining the baseline, `R=8,G=6`, and operating-envelope result;
- sharpening the final paragraph of Related Work into a precise novelty statement;
- reporting the matched-seed confidence intervals/effect sizes in Results rather than only ratios;
- ensuring Discussion separates design implications from implemented mechanisms;
- keeping Limitations adjacent to the strongest system-level claims;
- replacing all run-#1 provenance with the frozen run-#3 evidence;
- checking every reference against the verified literature matrix/full text before submission.

## Submission gate

The paper is evidence-ready when all of the following hold:

- manuscript numerical claims match the frozen run #3 artifact;
- matched-seed statistics are present in the Results section;
- reproducibility note names run #3 and its artifact digest;
- no unsupported measurement/standard/MIMO/Mode-2 claims are introduced;
- venue-specific page/template constraints are applied only after the scientific text is frozen.
