# Frozen matched-seed Results insert

Use the following evidence in Section 5.4 of `MANUSCRIPT.md` when replacing the current placeholder about statistics being generated automatically.

At `N=100`, the `R=8, G=6 dB` configuration improves mean first-transmission success over the `R=1, G=0 dB` baseline by `0.516358` across 100 matched deterministic seeds (95% CI `[0.505829, 0.526887]`, Cohen's `dz=9.6122`, paired-t `p=1.4474e-99`). Mean expected PHY goodput increases by `1.870079 Mbps` (95% CI `[1.728555, 2.011603]`, Cohen's `dz=2.5899`, paired-t `p=6.9415e-46`). These are matched-seed `DERIVED_SYSTEM_LEVEL_METRIC` comparisons under the evaluated model, not measurements.

The corresponding scenario means are `0.013 -> 0.529` for first-TX success and `0.359 -> 2.229 Mbps` for expected PHY goodput. The mean SINR changes from `-23.03 dB` to `0.53 dB`.
