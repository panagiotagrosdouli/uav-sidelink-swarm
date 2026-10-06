# Zenodo preprint deposit metadata

Prepared: 2026-10-06

Use this file as the copy/paste source when creating the Zenodo record.

## Deposit type

**Resource type:** Publication / Preprint

**Version:** v1.0-preprint

**Language:** English

## Title

**Topology-Conditioned Interference and Resource-Isolation Trade-offs in 5G NR Sidelink UAV Swarms**

## Creator

**Panagiota Grosdouli**

Affiliation:

**Department of Electrical and Computer Engineering, Democritus University of Thrace, Xanthi, Greece**

Do not add additional authors.

## Abstract / description

Direct NR sidelink is a candidate for infrastructure-independent UAV-swarm communication, but dense aerial line-of-sight conditions make scalability depend on more than swarm size alone. We present a measurement-grounded, NR-aware system-level study of communication topology, exact frequency-resource partitioning, and directional desired/interferer selectivity. A 100-seed campaign evaluates N in {5,10,20,30,50,75,100}, partitions a 133-PRB profile over R in {1,2,4,8} abstract orthogonal resources, and tests G in {0,3,6,9} dB relative desired/interferer advantage. Under the full-load sequential-disjoint baseline, N=100 yields -23.03 dB mean SINR, 0.0128 first-transmission success probability, and 0.359 Mbps expected PHY goodput. Yet greedy short-link pairing at the same N, R=1, G=0 reduces mean desired-link length from 517 m to 84 m and raises success probability to 0.4766 and goodput to 15.116 Mbps. Resource partitioning and spatial selectivity expand the evaluated reliability-goodput region, but partitioning exhibits a non-monotonic interference/bandwidth trade-off. The results therefore support topology-conditioned operating regions rather than a universal density-only swarm-capacity claim.

## Keywords

- 5G NR sidelink
- UAV swarm
- topology
- interference
- resource isolation
- link adaptation
- reliability-goodput operating region
- reproducibility

## Related resource

GitHub repository:

https://github.com/panagiotagrosdouli/uav-sidelink-swarm

Relation: software / supplementary research artifact supporting the preprint.

## File to upload

Upload:

`paper/vtc2027/VTC2027_Spring_UAV_Sidelink.pdf`

Use the CI-published PDF from the current `main` branch.

The independently checked PR-build artifact had:

- artifact ID: `11441543166`
- SHA-256: `fd59ca7b9e039690a3b683c8ef8c74b564ffabf87012f155a9371b87951a13a5`
- pages: 5
- page size: US Letter (612 x 792 pt)
- encryption: none
- visual render check: passed at 180 dpi

## DOI workflow

For a first Zenodo deposit with no existing DOI for this manuscript:

1. Answer **No** to “Do you already have a DOI for this upload?”
2. Use **Get a DOI now!** if you want to reserve the DOI before publication.
3. Save the record as a draft.
4. Do not delete the draft after reserving the DOI, because the reservation would be lost.
5. Publish only after the final metadata, PDF, and license are confirmed.

## License

**Author decision required.**

Do not auto-select a license from this repository metadata. The repository currently has no root software `LICENSE`, and the manuscript license on Zenodo is a separate decision.

## Publication status note

This is a **preprint**. It is not peer-reviewed, accepted, or a proceedings publication at the time of this metadata packet.

## Scientific claim guardrails

Do not describe:

- simulation/model-derived RF results as field measurements;
- the conflict-graph allocator as normative 3GPP Mode 1/Mode 2;
- G as measured antenna/beamforming gain;
- expected PHY goodput as application throughput;
- 5G-LENA BLER curves as UAV measurements or normative 3GPP BLER tables;
- N=100 as a universal supported swarm capacity;
- topology control itself as the novelty.

Preferred novelty wording:

> Prior studies have examined UAV sidelink, interference, topology control, resource allocation, and link adaptation under different abstractions. This work jointly characterizes topology-conditioned interference scaling, bandwidth-aware NR resource isolation, and the resulting reliability-goodput operating region in a controlled reproducible UAV-sidelink system-level study.
