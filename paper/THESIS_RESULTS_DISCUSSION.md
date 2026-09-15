# Results

All RF/network quantities reported in this section are simulation/model-derived unless explicitly stated otherwise.

## Density scaling

With one shared frequency resource and no directional advantage, mean SINR decreases from -0.49 dB at N=5 to -23.03 dB at N=100. At N=100, mean first-transmission success is 0.0128 and expected PHY goodput is 0.359 Mbps.

The failure diagnostic indicates that the dense regime is predominantly aggregate-interference limited. Approximately 72.4% of policy-failed links at N=100 are classified as aggregate-interference dominated, compared with 27.6% classified as dominant-interferer failures. This indicates that increasing swarm density shifts the system toward a many-interferer regime rather than one dominated by isolated strong interferers.

## Frequency-resource separation

At N=100 and G=0 dB, exact PRB partitioning produces the following mean results:

| Resources R | Mean SINR (dB) | First-TX success | Expected PHY goodput (Mbps) |
|---:|---:|---:|---:|
| 1 | -23.03 | 0.0128 | 0.359 |
| 2 | -16.20 | 0.0749 | 0.668 |
| 4 | -10.48 | 0.0775 | 0.572 |
| 8 | -5.47 | 0.2049 | 1.042 |

Increasing the number of resources reduces co-channel interference but also reduces the PRBs and transport-block size available to each link. Consequently, expected goodput is not monotonic with resource partitioning. In particular, R=4 improves mean SINR relative to R=2 while reducing expected goodput from 0.668 to 0.572 Mbps. At R=8, the interference reduction is sufficient for both first-transmission success and expected goodput to exceed the study's engineering-policy thresholds at N=100.

## Directional relative advantage

At N=100 with R=1, increasing the experimental directional relative advantage G from 0 to 9 dB changes mean SINR from -23.03 to -14.03 dB and expected PHY goodput from 0.359 to 1.435 Mbps. First-transmission success, however, reaches only 0.0494 at G=9 dB and remains below the 0.10 reliability threshold. Thus, in the densest shared-resource configuration, directional advantage alone improves link quality and goodput but does not recover the required first-transmission reliability.

## Combined resource separation and directional selectivity

At N=100, representative mitigation configurations are:

| R | G (dB) | Mean SINR (dB) | First-TX success | Expected PHY goodput (Mbps) |
|---:|---:|---:|---:|---:|
| 1 | 0 | -23.03 | 0.0128 | 0.359 |
| 8 | 0 | -5.47 | 0.2049 | 1.042 |
| 2 | 6 | -10.20 | 0.1262 | 1.414 |
| 4 | 6 | -4.48 | 0.2193 | 1.608 |
| 8 | 6 | 0.53 | 0.5292 | 2.229 |
| 8 | 9 | 3.53 | 0.8050 | 3.493 |

The strongest evaluated combined configuration, R=8 and G=9 dB, reaches 0.8050 first-transmission success and 3.493 Mbps expected PHY goodput at N=100. The R=8, G=6 dB configuration reaches 0.5292 first-transmission success and 2.229 Mbps expected PHY goodput.

Relative to the R=1,G=0 baseline, R=8,G=6 increases mean first-transmission success by 0.516358 across 100 matched deterministic seeds (95% CI [0.505829, 0.526887], Cohen's dz=9.6122, paired-t p=1.4474e-99). Mean expected PHY goodput increases by 1.870079 Mbps (95% CI [1.728555, 2.011603], Cohen's dz=2.5899, paired-t p=6.9415e-46). These statistics are matched-seed system-level comparisons under the evaluated model, not independent measurements.

## Evaluated operating envelope

Using the explicit engineering-policy requirements of mean first-transmission success >= 0.10 and mean expected PHY goodput >= 1 Mbps, the largest evaluated feasible swarm sizes are:

| Resources R | G=0 dB | G=3 dB | G=6 dB | G=9 dB |
|---:|---:|---:|---:|---:|
| 1 | 10 | 10 | 20 | 50 |
| 2 | 50 | 75 | 100 | 100 |
| 4 | 50 | 75 | 100 | 100 |
| 8 | 100 | 100 | 100 | 100 |

These values describe the boundary of the evaluated grid. Because N=100 is the largest simulated swarm size, an entry of 100 means that the policy targets remain satisfied at the largest evaluated point; it does not establish a universal maximum swarm capacity or demonstrate feasibility beyond N=100.