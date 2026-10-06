# Submission plan

Checked: 2026-10-06.

## Primary target: IEEE VTC2027-Spring

The official VTC2027-Spring call for papers now lists a **final regular-paper extension to 14 October 2026**, so this venue remains actionable. The conference will be held in Hamburg, Germany, 20–23 June 2027.

**Why it fits:** the CFP explicitly includes Emerging Technologies / 6G and Beyond; IoT, M2M, Sensor Networks and Ad-Hoc Networking; Radio Access Technology; Space, Non-terrestrial, Airborne and Maritime Mobile Systems and Services; and Spectrum Management. The paper's topology-conditioned aerial sidelink interference and resource-management contribution fits these tracks without claiming a standards-complete Mode-1/Mode-2 implementation.

- Current regular-paper deadline: **14 October 2026 (final extension)**.
- Nominal paper length: **5 pages**.
- Up to 2 additional pages are permitted with overlength charges under the current CFP.
- Submission should use the topology-first manuscript narrative and the frozen scientific evidence.

## Backup target: IEEE VTC2027-Fall

VTC2027-Fall is scheduled for Osaka, Japan, 27–30 September 2027. The official conference site lists:

- regular-paper deadline: **1 February 2027**;
- acceptance notification: **14 April 2027**.

This is the cleanest backup if supervisor/co-author review or IEEE-template conversion cannot be completed for the Spring deadline.

## Scientific positioning

The paper should be framed around one central statement:

> Swarm density alone is not a sufficient predictor of UAV sidelink scalability; the operating regime is conditioned by communication topology, and resource isolation must be evaluated together with its PRB/TBS bandwidth cost.

The three supported contributions are:

1. topology-conditioned interference scaling using matched-seed sequential versus nearest-neighbour pairing;
2. exact resource-isolation cost/benefit, including the non-monotonic R=2 -> R=4 goodput result;
3. a joint reliability/goodput operating envelope over resource separation and experimental spatial selectivity, with allocator, link-adaptation, and noise-bandwidth robustness checks.

## Immediate submission sequence

1. Keep the scientific campaign frozen; do not add features merely for submission.
2. Use the revised topology-first paper/MANUSCRIPT_SUBMISSION.md.
3. Compress into the IEEE VTC template around 3 main figures and 2 compact tables.
4. Keep routing, AMOVFLY, traffic, full HARQ, ULA, and thesis-wide ablation out of the 5-page narrative.
5. Verify every bibliography entry against DOI/publisher metadata.
6. Run a final manuscript-to-evidence claim audit.
7. Obtain supervisor/co-author approval of title, author list, affiliations, and final submission version.

## Reviewer-risk controls

The final manuscript must explicitly state that:

- the baseline density collapse is topology-conditioned, not universal;
- the weighted conflict-graph allocator is a THIS_WORK abstraction, not normative NR Mode 1/2;
- the directional variable G is a sensitivity parameter, not measured beamforming gain;
- BLER evidence comes from 5G-LENA link-level simulation, not UAV measurements or 3GPP BLER tables;
- expected PHY goodput is not end-to-end application throughput;
- N=100 is the largest evaluated point, not a universal swarm-capacity limit.

The selected venue changes page constraints and editorial emphasis, not the underlying scientific evidence.