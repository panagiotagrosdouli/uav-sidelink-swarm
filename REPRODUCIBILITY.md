# Reproducibility Guide

## Scope

This repository is a research software artifact for system-level evaluation of 5G NR sidelink communication in UAV swarms. Its numerical RF/network results are simulation/model-derived unless a result is explicitly identified as measured telemetry.

## Canonical evidence

The current broader canonical research campaign is tied to scientific commit:

`fcae537ef0846b94c0c73ce306e15c406ab542f7`

The recorded final campaign reports:

- 18/18 registered experiments successful;
- 17/17 canonical figures present;
- 304 scientific audit checks;
- 0 scientific audit failures;
- 100 deterministic Monte-Carlo seeds for the main full-campaign studies.

Paper-specific numerical claims must follow the frozen paper experiment described in `paper/README.md` and `paper/MANUSCRIPT_SUBMISSION.md`. Similar-looking values from different experiment families must not be mixed.

## Environment

Install the Python dependencies:

```bash
pip install -r requirements.txt
```

Run the validation suite:

```bash
python -m pytest -q
```

## Automated research workflows

The repository includes GitHub Actions workflows for research execution and evidence generation, including:

- `.github/workflows/final-campaign.yml` — canonical campaign execution, evidence finalization, and scientific audit;
- `.github/workflows/amovfly-public-pair.yml` — public AMOVFLY mobility evidence pipeline.

## Evidence classes

Important quantities are explicitly classified using provenance categories such as:

- `MEASURED` / `MEASURED_DATASET`
- `STANDARD`
- `LITERATURE`
- `LINK_LEVEL_SIMULATION`
- `DERIVED`
- `DERIVED_SYSTEM_LEVEL_METRIC`
- `EXPERIMENTAL_SWEEP`
- `EXPERIMENTAL_CONFIGURATION`
- `THIS_WORK`

This separation is intended to prevent simulated or derived results from being presented as field measurements or standards-defined performance.

## Scientific limitations

The repository does not claim a bit-accurate NR sidelink PHY, measured multi-UAV RF interference/PDR, normative Mode-1/Mode-2 scheduling, full MIMO/beam management, or a universal maximum UAV swarm size.

## Citation

Until a formal paper publication record exists, cite the repository/software artifact using `CITATION.cff`. After acceptance/publication, add the official venue, year, pages, DOI, and complete author list as the preferred paper citation while retaining the software citation for the reproducibility artifact.
