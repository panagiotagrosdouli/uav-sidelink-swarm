# UAV Sidelink Swarm

**Research software, paper source, and reproducibility package for topology-conditioned interference and resource-isolation studies in 5G NR sidelink UAV swarms.**

## Paper

**Topology-Conditioned Interference and Resource-Isolation Trade-offs in 5G NR Sidelink UAV Swarms**

**Author:** Panagiota Grosdouli  
**Affiliation:** Department of Electrical and Computer Engineering, Democritus University of Thrace, Xanthi, Greece  
**Status:** preprint-ready research manuscript; **not peer-reviewed, accepted, or formally published** unless this repository is updated with a publication record.

- [CI-verified 5-page PDF](paper/vtc2027/VTC2027_Spring_UAV_Sidelink.pdf)
- [IEEE LaTeX source](paper/vtc2027/main.tex)
- [Full manuscript](paper/MANUSCRIPT_SUBMISSION.md)
- [Paper evidence and scope](paper/README.md)
- [Reproducibility guide](REPRODUCIBILITY.md)
- [Scientific readiness audit](docs/FINAL_READINESS.md)
- [Citation metadata](CITATION.cff)

> All RF/network performance values are simulation/model-derived unless explicitly identified as measured telemetry. The project does **not** claim measured multi-UAV RF performance.

## Research question

> How do communication topology and swarm density jointly determine the UAV sidelink interference regime, and when do bandwidth-aware resource isolation and spatial selectivity expand the evaluated reliability-goodput operating region?

The central result is that **swarm size alone is not a sufficient predictor of sidelink scalability**. Desired-link topology can change the operating regime dramatically, while frequency isolation must be evaluated together with its PRB/TBS bandwidth cost.

## Headline results

### 1. Topology is a first-order scaling variable

At `N=100, R=1, G=0`, changing only the pairing topology gives:

| Pairing | Mean desired distance | Mean SINR | First-TX success | Expected PHY goodput |
|---|---:|---:|---:|---:|
| Sequential disjoint | 517.20 m | -23.03 dB | 0.0128 | 0.359 Mbps |
| Greedy short-link | 84.05 m | -1.75 dB | 0.4766 | 15.116 Mbps |

**Interpretation:** the severe long-link baseline degradation is not a topology-independent density law.

### 2. Resource isolation is not free

At `N=100, G=0`:

| Resources R | Mean SINR | First-TX success | Expected PHY goodput |
|---:|---:|---:|---:|
| 1 | -23.03 dB | 0.0128 | 0.359 Mbps |
| 2 | -16.20 dB | 0.0749 | 0.668 Mbps |
| 4 | -10.48 dB | 0.0775 | 0.572 Mbps |
| 8 | -5.47 dB | 0.2049 | 1.042 Mbps |

The `R=2 -> R=4` point is central: SINR improves while expected goodput decreases because additional isolation also reduces the PRBs/TBS available to each link.

### 3. Resource isolation and spatial selectivity are complementary

At `N=100`, the sequential baseline `R=8, G=6 dB` reaches:

- mean SINR: **0.53 dB**
- first-TX success: **0.5292**
- expected PHY goodput: **2.229 Mbps**

Relative to `R=1, G=0` under matched seeds:

- success difference: **+0.516358**, 95% CI **[0.505829, 0.526887]**
- expected-goodput difference: **+1.870079 Mbps**, 95% CI **[1.728555, 2.011603]**

These results define an **evaluated operating region**, not a universal UAV-capacity limit.

## What is new here

The novelty is **not** the generic use of sidelink, topology control, interference analysis, or resource allocation in UAV networks. Prior work has studied each of those areas.

This project instead provides a controlled, reproducible **NR-aware operating-region characterization** combining:

- topology-conditioned interference scaling;
- exact PRB partitioning with recomputed TBS/LDPC/BLER behavior;
- reliability-goodput trade-offs rather than SINR-only conclusions;
- resource isolation together with an experimental spatial desired/interferer advantage;
- matched-seed robustness checks over pairing, allocator, link adaptation, and noise-bandwidth accounting.

## Paper-specific system model

| Parameter | Value / role |
|---|---|
| Carrier | 3.5 GHz |
| Nominal bandwidth | 50 MHz |
| SCS | 30 kHz |
| PRBs | 133 |
| UAV area | 1000 m x 1000 m |
| Altitude | 100 m |
| Tx power | 30 dBm |
| Noise figure | 7 dB |
| Swarm sizes | `N={5,10,20,30,50,75,100}` |
| Resource partitions | `R={1,2,4,8}` |
| Spatial sensitivity | `G={0,3,6,9} dB` |
| Main Monte Carlo | 100 deterministic matched seeds |
| Propagation | published measurement-derived 3.5 GHz A2A large-scale fit |
| Link evaluation | NR MCS/TBS/LDPC mechanics + sourced 5G-LENA v5.0 link-level BLER data |

For swarm size `N`, each static snapshot contains `floor(N/2)` simultaneously active one-way disjoint links.

## Scientific scope and limitations

This is an **NR-aware system-level model**, not a standards-complete NR sidelink implementation.

The repository does not claim:

- measured multi-UAV RF interference, BLER, PDR, or end-to-end latency;
- a bit-accurate sidelink PHY;
- normative Mode-1/Mode-2 scheduling or sensing;
- full fast fading, MIMO, beam tracking, or beam management;
- measured beamforming gain;
- a universal maximum supported swarm size.

The weighted conflict-graph allocator and adaptive MCS policy are `THIS_WORK` abstractions. The directional parameter `G` is an experimental desired/interferer sensitivity variable. Expected PHY goodput is not application-layer throughput.

## Reproducibility

```bash
pip install -r requirements.txt
python -m pytest -q
python -m tools.run_thesis_pipeline --dry-run
```

The topology-first IEEE paper revision passed:

- figure generation;
- citation-key integrity;
- LaTeX compilation;
- undefined citation/reference checks;
- exact 5-page limit;
- overfull-box checks;
- reviewer-robustness validation;
- scientific CI.

The verified PDF is committed at [`paper/vtc2027/VTC2027_Spring_UAV_Sidelink.pdf`](paper/vtc2027/VTC2027_Spring_UAV_Sidelink.pdf).

## Evidence provenance

Two evidence contexts are intentionally kept separate.

**Paper-specific evidence** supports the topology/resource/spatial-selectivity claims in the manuscript. The 100-seed reviewer-hardening campaign is documented in [`docs/experiments/013_reviewer_robustness.md`](docs/experiments/013_reviewer_robustness.md).

**Broader research evidence** contains the larger 18-experiment campaign, including HARQ, routing, mobility, traffic, ULA sensitivity, channel comparisons, and ablations. Its readiness gate is [`docs/FINAL_READINESS.md`](docs/FINAL_READINESS.md).

Do not substitute numerical results between these contexts without checking the exact experiment definition.

## Repository structure

```text
paper/                  manuscript, IEEE source, paper audit material
simulations/            system-level experiments
results/                generated experiment outputs
figures/                generated research figures
references/             bibliography and provenance records
docs/experiments/       experiment definitions and run evidence
tools/                  reproducibility and audit tooling
tests/                  validation tests
```

## Citation

Until a paper/preprint DOI exists, cite the repository/software artifact using [`CITATION.cff`](CITATION.cff).

After a public preprint DOI is created, this README and `CITATION.cff` should be updated with the permanent DOI and preferred paper citation.

## License

A repository-wide software license has **not yet been declared**. This does not prevent depositing the manuscript as a preprint under a separately selected publication license, but a software license should be chosen before encouraging third-party code reuse.

## Core external evidence

- U. Erdemir et al., *IEEE VTC 2023-Spring*, DOI `10.1109/VTC2023-Spring57618.2023.10199853`.
- D. Mishra et al., *Computer Communications* 192 (2022), DOI `10.1016/j.comcom.2022.06.001`.
- W. J. Lau et al., *Computer Networks* 229 (2023), DOI `10.1016/j.comnet.2023.109752`.
- M. M. Alam and S. Moh, *IEEE Transactions on Mobile Computing* 23(12) (2024), DOI `10.1109/TMC.2024.3403890`.
- H. Bai et al., *IEEE Wireless Communications Letters* 15 (2026), DOI `10.1109/LWC.2026.3658510`.
- N. Patriciello et al., *Simulation Modelling Practice and Theory* 96 (2019), DOI `10.1016/j.simpat.2019.101933`.
- CTTC 5G-LENA v5.0 software archive, DOI `10.5281/zenodo.21165297`.
