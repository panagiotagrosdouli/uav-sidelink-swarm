# VTC2027-Spring final submission checklist

## Scientific integrity

- [x] Main 100-seed operating-envelope campaign completed successfully.
- [x] 100-seed topology/allocator/link-adaptation/noise-bandwidth robustness campaign completed successfully.
- [x] Active-link semantics are explicit: `floor(N/2)` simultaneous one-way disjoint links per snapshot.
- [x] Topology-dependent density claim corrected after robustness testing.
- [x] Random-allocation and fixed-MCS controls included.
- [x] Paired-bootstrap confidence intervals included for the main matched-seed comparison.
- [x] Expected PHY goodput is explicitly defined and separated from application/network throughput.
- [x] Operating-envelope thresholds are identified as mean point-estimate engineering policies, not guarantees.
- [x] Resource-grid, perfect-orthogonality, allocator, MCS-adaptation, and directional-gain abstractions are explicit.
- [x] 5G-LENA curves are identified as generic NR EESM link-level simulation evidence, not PSSCH measurements/standards.
- [x] Channel measurement domain and synthetic-distance extrapolation are stated.
- [x] Weak failure-composition figure removed; retained N=100 classification is labeled heuristic.

## Paper QA

- [x] IEEE conference two-column layout.
- [x] References and DOIs/standard metadata checked against publisher/repository records.
- [x] No missing or unused citation keys in the audited source.
- [x] AI-editing disclosure aligned with the VTC policy.
- [x] Figures regenerate from committed CSV extracts.
- [ ] Final branch CI confirms exactly 5 pages.
- [ ] Final branch CI confirms no overfull boxes.
- [ ] Final branch CI confirms no undefined citations/references.
- [ ] Final PDF rendered and visually inspected after the audit merge.

## Human confirmation before upload

- [ ] Confirm final author list and author order.
- [ ] Confirm corresponding-author email.
- [ ] Confirm exact affiliation wording required by the university/supervisor.
- [ ] Obtain supervisor/co-author approval of the scientific claims and final PDF.
- [ ] Recheck the official VTC2027-Spring CFP and submission portal immediately before upload.
- [ ] Verify track/topic selection in the submission system.
- [ ] Run final PDF compliance check required by the venue, if provided.
- [ ] Upload the final PDF only after the preceding items are confirmed.
