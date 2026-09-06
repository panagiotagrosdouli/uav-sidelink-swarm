# Evidence-backed key findings

This file is generated from final-campaign result tables. Values are simulation/derived unless explicitly stated otherwise.

- **Scaling (fixed_area)**: mean SINR changes from 7.52 dB at N=5 to -1.75 dB at N=100; final-point 95% CI [-1.89, -1.61] dB.
- **Scaling (fixed_density)**: mean SINR changes from 7.53 dB at N=5 to -1.75 dB at N=100; final-point 95% CI [-1.89, -1.61] dB.
- **Ablation at N=100**: highest mean modeled goodput among evaluated mechanisms is `adaptive_directional6_shared` at 0.316 Mbps. This is system-level modeled goodput, not measured throughput.
- **Resource allocation at N=50**: highest mean derived PHY goodput in the evaluated grid occurs for `greedy` with 8 resources (1.471 Mbps).

## External/missing evidence

- Real AMOVFLY canonical figure is unavailable because raw external telemetry is not vendored; run `real_mobility_pair` with user-supplied AMOVFLY files.
