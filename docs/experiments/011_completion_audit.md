# Experimental completion audit

This audit follows the master experimental program and records what is already present on `main`, what is validated, and what still needs completion. It is an engineering/research log, not thesis prose.

| Capability | Implemented | Tested | Source-backed | Validated | Missing work |
|---|---:|---:|---:|---:|---|
| Measurement-derived A2A propagation | yes | yes | yes | yes | no raw RF samples available |
| 3GPP aerial large-scale channel | yes | yes | yes | partial | full fast fading intentionally out of scope |
| Common SINR/interference engine | yes | yes | mixed | yes | interference decomposition extensions |
| Density Monte Carlo | yes | yes | mixed | yes | fixed-density scaling; N=75/100 final campaign |
| Real AMOVFLY mobility loader | yes | yes | yes | partial | common global coordinate frame required |
| Resource allocation | yes | yes | algorithm = THIS_WORK | yes | graph-coloring baseline + fairness |
| Routing | yes | yes | algorithm = THIS_WORK | yes | route reliability/latency under mobility |
| Directional gain sensitivity | yes | yes | sweep | yes | desired gain vs interference suppression separation |
| NR MCS Table 1 | yes | yes | STANDARD | yes | none for Table 1 entries 0..28 |
| 5G-LENA BLER | partial | yes | LINK_LEVEL_SIMULATION | partial | importer must extract BG1+BG2/all available CBS/MCS; full dataset not vendored |
| Link adaptation | yes | yes | THIS_WORK | partial | fixed-vs-adaptive final campaign |
| TBS | yes | yes | STANDARD | yes | independent spot validation retained |
| LDPC BG/CBS | yes | yes | STANDARD | yes | none known |
| HARQ | Chase abstraction | yes | DERIVED | partial | exact IR/CC history processing remains external 5G-LENA task |
| Sidelink overhead | yes | yes | mixed | yes | exact profile remains scenario configuration |
| Reproducibility pipeline | yes | yes | n/a | yes | final campaign freeze + canonical manifest |
| Fairness | no | no | formula known | no | implement Jain index |
| Fixed-area vs fixed-density scaling | no | no | SYNTHETIC | no | implement |
| Activity-factor study | no | no | EXPERIMENTAL_SWEEP | no | implement |
| Geometry families | limited | limited | SYNTHETIC | no | grid/circle/cluster/leader-follower |
| Final campaign bundle | no | no | mixed | no | implement after completion layers |

## Scientific blockers / non-claims

- The repository does not contain raw UAV RF swarm measurements; therefore simulated BLER/PDR/latency cannot be labelled measured.
- The full upstream 5G-LENA GPL C++ source is not vendored. The project will improve the importer so users can derive complete local numerical tables from an official source checkout.
- Exact NR HARQ Incremental Redundancy history processing is not recreated with an invented gain. Exact IR remains delegated to upstream 5G-LENA/ns-3 unless a faithful sourced implementation is added.
- AMOVFLY local `gps_x/gps_y/gps_z` coordinates must not be assumed to share a common origin across vehicles. Global latitude/longitude/altitude are the safer cross-UAV basis when available.

## Completion priorities

1. full BG1/BG2 5G-LENA Table-1 importer and metadata;
2. global-coordinate AMOVFLY processing;
3. fairness, geometry, activity and fixed-density scaling;
4. interaction/ablation experiments;
5. final canonical campaign, figures, tables and key findings.
