# Submission plan

Checked against the official venue pages: **2026-10-03**.

## Primary target: IEEE VTC2027-Spring

- Conference: IEEE VTC2027-Spring, Hamburg, Germany, 20–23 June 2027.
- Official regular-paper deadline: **14 October 2026 (extended)**.
- Regular paper: **5 pages** without overlength charge.
- Up to two additional pages are permitted with the conference's stated overlength charge.
- Relevant tracks include Emerging Technologies / 6G and Beyond; IoT, M2M, Sensor Networks and Ad-Hoc Networking / Cooperative Communication; Radio Access Technology; and Space, Non-terrestrial, Airborne and Maritime Mobile Systems and Services.

Official CFP: https://events.vtsociety.org/vtc2027-spring/call-for-papers-2/

## Positioning

The submission should **not** be positioned as a complete NR sidelink implementation or as a universal swarm-capacity study.

Recommended scientific framing:

> A reproducible, measurement-grounded and NR-aware characterization of how density, exact PRB partitioning, resource assignment, communication locality and directional spatial selectivity shape the evaluated UAV-sidelink reliability/goodput operating region.

The three contribution statements should remain:

1. measurement-grounded / NR-aware system evaluation;
2. controlled density-dependent interference characterization;
3. conditional exact-resource operating envelope with matched allocator and pairing robustness checks.

## Five-page content budget

### Page 1
Abstract + Introduction + concise contribution statement.

### Page 2
Closest Related Work + System Model + compact parameter table.

### Page 3
Exact resource/TBS/BLER methodology + statistical design + first main result.

### Page 4
Operating envelope + random-vs-conflict allocation sensitivity.

### Page 5
Pairing/locality sensitivity + Discussion + Limitations + Conclusion + References as space permits.

If the final IEEE layout cannot accommodate all evidence cleanly in five pages, an overlength version should only be considered after supervisor/co-author agreement.

## Main figures

Prefer three dense, publication-quality figures:

1. density scaling for baseline and selected mitigated configuration, with confidence information;
2. operating-envelope/resource-directionality result;
3. reviewer robustness figure combining or juxtaposing allocator and pairing sensitivity.

A fourth figure is justified only if the page budget remains readable.

## Material intentionally excluded from the main paper

Keep detailed HARQ, routing, AMOVFLY mobility, traffic-load analysis and thesis-wide ablations outside the main five-page narrative except for concise context. They remain valuable repository evidence but would dilute the specific paper contribution.

## AI-assistance policy

The official VTC2027-Spring conference policy states that AI tools may not be used in place of an author to generate article content. It permits AI tools to modify existing author-generated text, for example for grammar, and requires such use to be disclosed in the paper acknowledgements.

Official policy: https://events.vtsociety.org/vtc2027-spring/call-for-workshops-2/

For this project:

- human authors remain responsible for the scientific content, claims, authorship and final wording;
- automated assistance is used as research-code review, consistency checking, evidence organization and editing support;
- before submission, the human authors must ensure the final use is consistent with the venue policy and add an appropriate acknowledgement disclosure if required.

## Required work before upload

- freeze the reviewer-hardened scientific artifact and record it in `docs/experiments/013_reviewer_hardened_publication_evidence.md`;
- ensure every quantitative claim in `MANUSCRIPT_SUBMISSION.md` maps to that freeze;
- convert the text into the official IEEE conference template;
- include system parameters and conditional pairing/allocation assumptions explicitly;
- preserve random-allocation and nearest-neighbour sensitivity results;
- verify every reference against publisher/DOI metadata;
- confirm final author list/order, affiliations, corresponding author, funding and acknowledgements;
- confirm repository/software/data license;
- obtain supervisor/co-author approval;
- perform a final PDF visual audit, reference audit and claim audit.

## Release rule

No historical publication run should be treated as the current submission freeze after a scientific-model change. The final submitted PDF must point to the reviewer-hardened evidence record and must not silently mix results from the broader thesis campaign.
