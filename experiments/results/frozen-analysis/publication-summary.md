# Frozen Neural-Matrix Publication Summary

Models: 3 neural families; seeds: 20260912, 20260913, 20260914, 20260915, 20260916.

Values in parentheses are across-seed standard deviations. Deterministic baselines have no seed variation.

## Descriptive Zero-Shot External-Test Results

| Model | 1 h NMAE | 12 h NMAE | 24 h NMAE | 12 h CRPS | 12 h coverage error | 12 h mask Brier | 12 h rollout-state pressure violations/1,000 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Last observation carried forward | 0.3853 | 0.5753 | 0.6033 | NA | NA | NA | 5.3202 |
| Global median | 0.6634 | 0.6634 | 0.6698 | NA | NA | NA | 0.0000 |
| Hourly median | 0.6699 | 0.6617 | 0.6624 | NA | NA | NA | 0.0000 |
| Ridge vector autoregression | 0.3610 | 0.5301 | 0.5862 | NA | NA | NA | 0.6240 |
| Probabilistic GRU-D-style model | 0.3770 (0.0010) | 0.5216 (0.0013) | 0.5607 (0.0030) | 0.3850 (0.0008) | 0.0578 (0.0073) | 0.0617 (0.0020) | 161.0667 (6.5622) |
| Causally masked Transformer | 0.3768 (0.0016) | 0.5207 (0.0038) | 0.5591 (0.0062) | 0.3851 (0.0031) | 0.0327 (0.0123) | 0.0628 (0.0011) | 204.9199 (23.3724) |
| Recurrent state-space model | 0.4958 (0.0142) | 0.6220 (0.0047) | 0.6539 (0.0081) | 0.4957 (0.0065) | 0.4019 (0.0149) | 0.0645 (0.0004) | 2.4959 (1.2542) |

## External Recalibration

| Model | Horizon | Raw coverage | Recalibrated coverage | Raw width | Recalibrated width | Raw CRPS | Recalibrated CRPS | Raw Gaussian NLS | Recalibrated Gaussian NLS |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Probabilistic GRU-D-style model | 1 h | 0.8560 (0.0065) | 0.9002 (0.0047) | 1.4468 (0.0297) | 1.7049 (0.0304) | 0.2834 (0.0010) | 0.2886 (0.0005) | 0.8014 (0.0089) | 0.7754 (0.0113) |
| Probabilistic GRU-D-style model | 3 h | 0.8479 (0.0070) | 0.8818 (0.0021) | 1.6274 (0.0315) | 1.8255 (0.0167) | 0.3250 (0.0007) | 0.3278 (0.0006) | 0.9166 (0.0076) | 0.8972 (0.0023) |
| Probabilistic GRU-D-style model | 6 h | 0.8407 (0.0072) | 0.8891 (0.0058) | 1.7687 (0.0360) | 2.0733 (0.0516) | 0.3578 (0.0008) | 0.3622 (0.0018) | 1.0332 (0.0104) | 1.0081 (0.0049) |
| Probabilistic GRU-D-style model | 12 h | 0.8422 (0.0073) | 0.8841 (0.0027) | 1.9116 (0.0366) | 2.1839 (0.0190) | 0.3850 (0.0008) | 0.3885 (0.0012) | 1.1100 (0.0094) | 1.0874 (0.0050) |
| Probabilistic GRU-D-style model | 24 h | 0.8445 (0.0054) | 0.8828 (0.0041) | 2.0566 (0.0311) | 2.3218 (0.0253) | 0.4132 (0.0023) | 0.4165 (0.0022) | 1.1886 (0.0105) | 1.1670 (0.0077) |
| Causally masked Transformer | 1 h | 0.8540 (0.0085) | 0.9017 (0.0027) | 1.4372 (0.0443) | 1.7161 (0.0157) | 0.2828 (0.0015) | 0.2883 (0.0008) | 0.7829 (0.0064) | 0.7571 (0.0065) |
| Causally masked Transformer | 3 h | 0.8631 (0.0099) | 0.8796 (0.0015) | 1.7325 (0.0607) | 1.8318 (0.0115) | 0.3263 (0.0019) | 0.3278 (0.0012) | 0.8994 (0.0047) | 0.8930 (0.0051) |
| Causally masked Transformer | 6 h | 0.8597 (0.0114) | 0.8883 (0.0053) | 1.9066 (0.0789) | 2.1035 (0.0473) | 0.3581 (0.0023) | 0.3612 (0.0018) | 1.0117 (0.0067) | 1.0043 (0.0043) |
| Causally masked Transformer | 12 h | 0.8673 (0.0123) | 0.8866 (0.0034) | 2.1120 (0.1004) | 2.2555 (0.0346) | 0.3851 (0.0031) | 0.3874 (0.0021) | 1.0927 (0.0046) | 1.0886 (0.0071) |
| Causally masked Transformer | 24 h | 0.8731 (0.0118) | 0.8814 (0.0020) | 2.3192 (0.1256) | 2.3798 (0.0341) | 0.4147 (0.0052) | 0.4156 (0.0037) | 1.1801 (0.0059) | 1.1767 (0.0075) |
| Recurrent state-space model | 1 h | 0.5725 (0.0155) | 0.8960 (0.0045) | 0.9754 (0.0155) | 2.2572 (0.0533) | 0.3859 (0.0128) | 0.3793 (0.0102) | 2.2866 (0.1297) | 1.0545 (0.0268) |
| Recurrent state-space model | 3 h | 0.5317 (0.0124) | 0.8750 (0.0031) | 0.9915 (0.0183) | 2.3179 (0.0417) | 0.4310 (0.0085) | 0.4139 (0.0067) | 2.6574 (0.1407) | 1.1429 (0.0146) |
| Recurrent state-space model | 6 h | 0.5074 (0.0117) | 0.8800 (0.0033) | 1.0066 (0.0245) | 2.5481 (0.0452) | 0.4679 (0.0066) | 0.4464 (0.0054) | 3.0405 (0.1624) | 1.2215 (0.0093) |
| Recurrent state-space model | 12 h | 0.4981 (0.0149) | 0.8784 (0.0033) | 1.0269 (0.0396) | 2.6629 (0.0648) | 0.4957 (0.0065) | 0.4706 (0.0057) | 3.2856 (0.2625) | 1.2795 (0.0114) |
| Recurrent state-space model | 24 h | 0.4877 (0.0204) | 0.8779 (0.0022) | 1.0439 (0.0539) | 2.7861 (0.0415) | 0.5237 (0.0098) | 0.4951 (0.0075) | 3.6565 (0.3799) | 1.3469 (0.0118) |

The raw and recalibrated runs used identical split-specific Monte Carlo streams. Maximum patient-level NMAE difference was 4.768e-07; maximum mask-Brier difference was 0.000e+00.

## Frozen 12-Hour Paired NMAE Contrasts

| Split | Model A | Model B | A-B | 95% bootstrap interval | Patients |
| --- | --- | --- | ---: | ---: | ---: |
| internal_test | Probabilistic GRU-D-style model | Causally masked Transformer | 0.0021 | [0.0005, 0.0036] | 1806 |
| internal_test | Probabilistic GRU-D-style model | Ridge vector autoregression | -0.0131 | [-0.0167, -0.0093] | 1806 |
| internal_test | Causally masked Transformer | Ridge vector autoregression | -0.0152 | [-0.0194, -0.0113] | 1806 |
| internal_test | Recurrent state-space model | Ridge vector autoregression | 0.0839 | [0.0790, 0.0893] | 1806 |
| internal_test | Ridge vector autoregression | Last observation carried forward | -0.0423 | [-0.0496, -0.0340] | 1806 |
| external_test | Probabilistic GRU-D-style model | Causally masked Transformer | 0.0008 | [-0.0000, 0.0017] | 10178 |
| external_test | Probabilistic GRU-D-style model | Ridge vector autoregression | -0.0085 | [-0.0102, -0.0068] | 10178 |
| external_test | Causally masked Transformer | Ridge vector autoregression | -0.0093 | [-0.0114, -0.0074] | 10178 |
| external_test | Recurrent state-space model | Ridge vector autoregression | 0.0919 | [0.0896, 0.0942] | 10178 |
| external_test | Ridge vector autoregression | Last observation carried forward | -0.0452 | [-0.0488, -0.0414] | 10178 |

Negative contrast values favor model A. Intervals use a patient bootstrap after averaging the five fixed neural seeds. Across-seed variation is reported separately.

## Cross-Cohort 12-Hour NMAE Degradation

| Model | Internal | Zero-shot external | Absolute change [95% CI] | Relative change [95% CI] |
| --- | ---: | ---: | ---: | ---: |
| Last observation carried forward | 0.5525 | 0.5753 | 0.0228 [0.0115, 0.0349] | 4.1% [2.1%, 6.4%] |
| Global median | 0.6197 | 0.6634 | 0.0437 [0.0317, 0.0556] | 7.1% [5.0%, 9.1%] |
| Hourly median | 0.6180 | 0.6617 | 0.0437 [0.0314, 0.0558] | 7.1% [5.0%, 9.2%] |
| Ridge vector autoregression | 0.5102 | 0.5301 | 0.0198 [0.0102, 0.0289] | 3.9% [2.0%, 5.7%] |
| Probabilistic GRU-D-style model | 0.4971 | 0.5216 | 0.0245 [0.0155, 0.0337] | 4.9% [3.1%, 6.9%] |
| Causally masked Transformer | 0.4951 | 0.5207 | 0.0257 [0.0166, 0.0346] | 5.2% [3.3%, 7.1%] |
| Recurrent state-space model | 0.5941 | 0.6220 | 0.0278 [0.0165, 0.0384] | 4.7% [2.7%, 6.6%] |

## Rank Stability

| Type | Context | Comparison | Spearman mean [range] | Pairwise reversal mean [range] |
| --- | --- | --- | ---: | ---: |
| cross_horizon | external_test | 1h to 12h | 0.843 [0.821, 0.857] | 0.162 [0.143, 0.190] |
| cross_horizon | external_test | 1h to 24h | 0.829 [0.786, 0.857] | 0.171 [0.143, 0.190] |
| cross_horizon | internal_test | 1h to 12h | 0.886 [0.857, 0.893] | 0.105 [0.095, 0.143] |
| cross_horizon | internal_test | 1h to 24h | 0.864 [0.857, 0.893] | 0.133 [0.095, 0.143] |
| cross_site | 12h | internal_test to external_test | 0.993 [0.964, 1.000] | 0.010 [0.000, 0.048] |
| cross_site | 24h | internal_test to external_test | 0.979 [0.964, 1.000] | 0.029 [0.000, 0.048] |

## Training

| Model | Parameters | Best epoch, range | Validation loss, mean (SD) |
| --- | ---: | ---: | ---: |
| Probabilistic GRU-D-style model | 59,232 | 20-20 | 0.7332 (0.0013) |
| Recurrent state-space model | 93,320 | 7-20 | -1.2649 (0.3926) |
| Causally masked Transformer | 247,848 | 20-20 | 0.7169 (0.0013) |

Interpretation boundary: passive free-running forecasting only. The tables do not establish treatment effects, counterfactual validity, policy quality, clinical benefit, or deployment safety.
