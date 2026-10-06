# Public preprint / DOI readiness checklist

Prepared: 2026-10-06

## Current status

**Scientific manuscript:** ready for public preprint deposit within the stated model scope.

A conference submission is **not required** before a Zenodo deposit. The preprint can be published independently and receive its own DOI.

## Verified before deposit

- [x] Single author is explicit: Panagiota Grosdouli.
- [x] Paper title is consistent across the main manuscript and IEEE source.
- [x] Topology-conditioned novelty framing is used.
- [x] Density-only universal claims have been removed from the paper framing.
- [x] Paper-specific and broader thesis evidence are separated.
- [x] 100-seed topology/allocator/link-adaptation/noise-bandwidth robustness campaign is documented.
- [x] Expected PHY goodput is distinguished from application throughput.
- [x] Conflict-graph scheduling is identified as a THIS_WORK abstraction.
- [x] Directional G is identified as an experimental sensitivity variable.
- [x] 5G-LENA BLER evidence is identified as link-level simulation evidence.
- [x] N=100 is described as an evaluated grid boundary, not a universal capacity.
- [x] IEEE LaTeX source compiles.
- [x] Citation integrity passes.
- [x] Undefined-reference checks pass.
- [x] Five-page check passes.
- [x] Overfull-box check passes.
- [x] CI-published topology-first PDF exists in the repository.
- [x] Final PDF independently preflighted: 5 US-Letter pages, openable, unencrypted, fonts embedded, and no clipping/overlap/broken-glyph issue found in the 180-dpi visual render.
- [x] Latest audited PR-build artifact: `VTC2027-Spring-UAV-Sidelink-Draft`, artifact ID `11441543166`, digest `sha256:fd59ca7b9e039690a3b683c8ef8c74b564ffabf87012f155a9371b87951a13a5`.

## Recommended Zenodo metadata

- Resource type: **Publication / Preprint**
- Title: **Topology-Conditioned Interference and Resource-Isolation Trade-offs in 5G NR Sidelink UAV Swarms**
- Creator: **Panagiota Grosdouli**
- Affiliation: **Department of Electrical and Computer Engineering, Democritus University of Thrace, Xanthi, Greece**
- Language: English
- Version: **v1.0-preprint**
- Related identifier: GitHub repository URL
- Description: use the manuscript abstract

Recommended keywords:

- 5G NR sidelink
- UAV swarm
- topology
- interference
- resource isolation
- link adaptation
- reliability-goodput operating region
- reproducibility

## Author choices still open

- [ ] Publish immediately or first reserve the DOI and place it in a later PDF version.
- [ ] Select the manuscript license on Zenodo.
- [ ] Add ORCID if available.
- [ ] Confirm exact affiliation wording.
- [ ] Decide whether the GitHub code should receive a separate software license.

## Repository license note

The repository currently has no root LICENSE file. This does not block a paper/preprint DOI deposit because the manuscript record can carry its own license. It does matter for third-party code reuse, so a software license should be chosen separately before promoting the repository as reusable open-source software.

## After Zenodo publishes the DOI

Update:

1. root README with the preprint DOI and citation;
2. `CITATION.cff` with a preferred paper citation and DOI;
3. `paper/README.md` with the public preprint status;
4. the manuscript front matter if a later version should display the DOI;
5. a GitHub release/tag if the code snapshot should be tied to the paper version.
