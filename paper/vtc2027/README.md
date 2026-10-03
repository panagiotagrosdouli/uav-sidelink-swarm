# VTC2027-Spring submission draft

This directory contains the reproducible IEEE-style conference-paper draft:

**Interference Scaling, Resource Isolation, and Topology Sensitivity in 5G NR Sidelink UAV Swarms**

Current author block:
- Panagiota Grosdouli
- Department of Electrical and Computer Engineering
- Democritus University of Thrace
- Xanthi, Greece

## Target venue

IEEE VTC2027-Spring, Hamburg, Germany, 20–23 June 2027.

Checked on 2026-10-03 against the official VTC site: regular papers use a 5-page conference format and the regular-paper deadline is 14 October 2026. Venue requirements can change, so recheck the official CFP immediately before upload.

Official CFP:
https://events.vtsociety.org/vtc2027-spring/call-for-papers-2/

## Scientific evidence

The manuscript is based on the audited paper-operating-envelope workflow and reviewer-hardening campaign.

Scientific commit:
f224ba9e5f95a23a088db24479c67461fcf497e6

Workflow run:
paper-operating-envelope #26, run ID 37106664614

Artifact ID:
11267104157

Artifact digest:
sha256:f3e6fe8ffac63168d878447bfd61f297f442a55c20b742e4def0374027350099

The compact CSV files in `data/` are audited publication extracts. The current submission regenerates three figures; the legacy failure-regime extract is retained for provenance but is no longer used in the paper because its per-seed conditional-fraction aggregation was judged too easy to misinterpret.

## Bibliographic verification

The paper uses only references whose publication metadata were checked against publisher, institutional, Zenodo, or official 3GPP/ETSI sources. The verification record is stored in `CITATION_AUDIT.md`. External citations support background/standardization/provenance claims; manuscript numerical results remain attributed to the repository's audited simulation evidence.

## Local build

From paper/vtc2027:

    python make_figures.py
    pdflatex -interaction=nonstopmode -halt-on-error main.tex
    pdflatex -interaction=nonstopmode -halt-on-error main.tex

The expected output is exactly 5 pages.

## Scientific claim boundary

The paper reports system-level simulation/model-derived results. For swarm size `N`, only `floor(N/2)` one-way disjoint links are simultaneously active in a static snapshot. The resource grid, allocator, MCS adaptation, directional advantage, and frequency-resource orthogonality are explicit research abstractions; the paper does not claim measured multi-UAV RF performance, standards-complete Mode-1/Mode-2 scheduling, full fading/beam management, or a universal maximum swarm size.

## Before submission

Confirm the final author list, corresponding-author email, affiliations, supervisor/co-author approval, and the current VTC submission instructions. Do not add co-authors or contact details unless they have been explicitly confirmed.

The draft includes the venue-required acknowledgment that OpenAI ChatGPT was used as an editing assistant for language, compression, LaTeX formatting, and bibliographic organization. It was not used to generate simulation data; final scientific responsibility remains with the author.
