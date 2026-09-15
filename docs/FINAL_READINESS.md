# Final Readiness Audit

**Status: READY FOR THESIS / RESEARCH HANDOFF**

This document is the current readiness gate for `main`. Historical completion logs under `docs/experiments/` are retained as evidence and are not authoritative when they conflict with this audit.

## Verified canonical state

- Canonical scientific commit: `fcae537ef0846b94c0c73ce306e15c406ab542f7`
- Final-thesis-campaign workflow run: **#5** (`34038078332`)
- Workflow conclusion: **success**
- Registered experiments: **18/18 successful**
- Canonical figures: **17/17 present**
- Scientific audit checks: **304**
- Scientific audit failures: **0**
- Missing external/optional evidence: **0**
- Main full-campaign Monte-Carlo studies: **100 deterministic seeds**
- README canonical artifact digest: `sha256:a0dbfbeaa24a371502a584ecf137c65df8a1afd7af23f038ee40ad3cede33e47`

The canonical workflow is recorded as successful for the canonical commit. The repository README records the same final-campaign status.

## Completion matrix

| Area | Status | Assessment |
|---|---|---|
| A2A measurement-derived propagation | READY | Source-backed model and validation present |
| 3GPP aerial large-scale channel | READY* | Auditable large-scale implementation; fast fading remains out of scope |
| SINR / interference engine | READY | Implemented and validated |
| Density Monte Carlo | READY | Canonical campaign completed |
| Scaling / geometry / activity | READY | Included in the final registered suite |
| AMOVFLY mobility processing | READY* | Common WGS84/ECEF/ENU path implemented; raw RF claims are excluded |
| Resource allocation | READY | Random/greedy/conflict-graph research abstractions evaluated |
| Routing | READY* | System-level graph abstraction, not a standardized NR routing protocol |
| Directionality / ULA sensitivity | READY* | Explicit sensitivity model, not full MIMO/beam management |
| NR MCS Table 1 | READY | MCS 0–28 covered |
| 5G-LENA BLER evidence | READY* | Official v5.0 Table-1 source preparation and provenance recorded |
| Link adaptation | READY* | Explicitly classified as THIS_WORK |
| TBS / LDPC / CBS | READY | Standards-based mechanics implemented and tested |
| HARQ | READY* | Ideal Chase abstraction; exact IR/CC history is out of scope |
| Sidelink resource overhead | READY | Scenario configuration is explicit |
| Fairness | READY | Jain fairness included in final results |
| Reproducibility | READY | Registry, manifest, provenance, artifacts and CI present |
| Statistical analysis | READY | Paired matched-seed comparisons and confidence intervals present |
| Final campaign | READY | 18/18 experiments completed and audited |

`*` READY means ready for the stated research scope, not standards-complete or field-validated.

## Scientific acceptance criteria

The project is acceptable for thesis/paper use when claims remain inside the evidence boundary:

1. Simulation/model-derived RF/network quantities must not be described as field measurements.
2. The resource allocators must be described as `THIS_WORK` system-level abstractions, not normative Mode-1/Mode-2 schedulers.
3. Directionality must be described as an experimental sensitivity model rather than full MIMO or beam management.
4. Routing results must be described as graph/path feasibility under the stated isolated-link abstraction.
5. HARQ must be described as an ideal Chase-combining abstraction unless an external bit-accurate 5G-LENA/ns-3 run is supplied.
6. The operating-envelope thresholds are experimental engineering policy targets, not 3GPP requirements.
7. AMOVFLY telemetry supports mobility/trajectory evidence; it does not by itself provide measured swarm RF interference, BLER, PDR or end-to-end latency.

## Reproduction gate

From a clean checkout:

```bash
pip install -r requirements.txt
python -m pytest -q
python -m tools.run_thesis_pipeline --dry-run
```

For the full registered campaign:

```bash
python -m tools.run_thesis_pipeline
```

For the canonical GitHub Actions evidence, use the `final-thesis-campaign` workflow recorded against the canonical scientific commit.

## Final verdict

**GREEN — the repository is ready to serve as the implementation and reproducibility package for the thesis/research paper within the documented scientific scope.**

No additional scientific feature should be added merely to call the project “complete”. Further work should be treated as a new research extension and should generate a new canonical campaign rather than silently changing the frozen evidence.
