# Submission plan

Checked: 2026-09-07.

## Primary target: IEEE VTC2027-Spring

**Why it fits:** the conference explicitly includes tracks on Emerging Technologies / 6G and Beyond; IoT, M2M, Sensor Networks and Ad-Hoc Networking; Radio Access Technology; Spectrum Management; and Space, Non-terrestrial, Airborne and Maritime Mobile Systems and Services. The UAV-sidelink operating-envelope paper fits these tracks naturally without stretching the contribution toward AI or a standards-complete implementation.

- Conference: IEEE VTC2027-Spring, Hamburg, Germany, 20–23 June 2027.
- Regular paper deadline checked on 2026-09-07: 30 September 2026 (extended deadline announced by IEEE VTS).
- Regular paper length announced in the CFP: 5 pages.

## Backup target: IEEE ICC 2027

- Conference: IEEE ICC 2027, Washington, DC, 30 May–3 June 2027.
- Technical-paper deadline checked on 2026-09-07: 2 October 2026.
- Strong venue, but the broad communications scope makes the positioning less UAV-specific than VTC.

## Fast alternative: IEEE WCNC 2027

- Conference: IEEE WCNC 2027, Panama City, 5–8 April 2027.
- Technical-paper deadline checked on 2026-09-07: 15 September 2026.
- Excellent wireless-networking fit, but the deadline leaves much less time for 5-page compression, template conversion, supervisor review, and final bibliography/figure checks.

## Recommended submission order

1. Prepare a VTC2027-Spring 5-page version as the primary manuscript.
2. Keep the frozen scientific evidence unchanged at publication run #3.
3. Compress the paper around three claims only: density-driven aggregate interference, exact PRB partitioning trade-off, and the cross-layer resource/directionality operating envelope.
4. Use 3–4 main figures maximum: baseline density scaling/failure regime; resource/directionality heatmap or operating-envelope figure; N=100 trade-off/effect-size result; optional resource-bandwidth trade-off.
5. Keep HARQ, routing, AMOVFLY mobility, traffic-load study, and full thesis ablation outside the main 5-page paper except as one-sentence context where necessary.
6. Obtain supervisor/co-author approval of title, author list, affiliations, and venue before final submission.

## Required editorial work before upload

- Convert `MANUSCRIPT_SUBMISSION.md` into the selected IEEE conference template.
- Reduce related work to the closest 4–6 papers.
- Replace Markdown tables with compact IEEE tables/figures.
- Ensure every quantitative claim maps to frozen run #3 evidence.
- Add figure captions that state metric classification and scenario assumptions where necessary.
- Verify final reference metadata against publisher/DOI records.
- Run a final claim audit against `docs/experiments/012_publication_evidence.md` and `paper/CLAIM_GUARDRAILS.md`.

The selected venue does not change the scientific result. It only determines manuscript length, formatting, and the amount of supporting material that can remain in the main paper.