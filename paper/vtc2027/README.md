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

The compact CSV files in data/ are publication extracts from that audited evidence and regenerate the four paper figures.

## Bibliographic verification

The paper uses only references whose publication metadata were checked against publisher, institutional, Zenodo, or official 3GPP/ETSI sources. The verification record is stored in `CITATION_AUDIT.md`. External citations support background/standardization/provenance claims; manuscript numerical results remain attributed to the repository's audited simulation evidence.

## Local build

From paper/vtc2027:

    python make_figures.py
    pdflatex -interaction=nonstopmode -halt-on-error main.tex
    pdflatex -interaction=nonstopmode -halt-on-error main.tex

The expected output is exactly 5 pages.

## Scientific claim boundary

The paper reports system-level simulation/model-derived results. It does not claim measured multi-UAV RF performance, normative Mode-1/Mode-2 scheduling, full fast fading, full MIMO/beam management, or a universal maximum swarm size. The completed robustness campaign shows that the severe baseline density collapse is topology-sensitive; this limitation is central to the paper rather than hidden.

## Before submission

Confirm the final author list, corresponding-author email, affiliations, supervisor/co-author approval, and the current VTC submission instructions. Do not add co-authors or contact details unless they have been explicitly confirmed.

The draft includes an acknowledgment disclosing the use of OpenAI ChatGPT for editing/compression and LaTeX formatting; scientific design, experiments, interpretation, source verification, and final responsibility remain with the author.
