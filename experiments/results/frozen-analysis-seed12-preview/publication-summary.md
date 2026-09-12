# Frozen Neural-Matrix Publication Summary

Models: 3 neural families; seeds: 20260912.

Values in parentheses are across-seed standard deviations. Deterministic baselines have no seed variation.

## Descriptive Zero-Shot External-Test Results

| Model | 1 h NMAE | 12 h NMAE | 24 h NMAE | 12 h CRPS | 12 h coverage error | 12 h mask Brier | 12 h rollout-state pressure violations/1,000 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Last observation carried forward | 0.3853 | 0.5753 | 0.6033 | NA | NA | NA | 5.3202 |
| Global median | 0.6634 | 0.6634 | 0.6698 | NA | NA | NA | 0.0000 |
| Hourly median | 0.6699 | 0.6617 | 0.6624 | NA | NA | NA | 0.0000 |
| Ridge vector autoregression | 0.3610 | 0.5301 | 0.5862 | NA | NA | NA | 0.6240 |
| Probabilistic GRU-D-style model | 0.3762 | 0.5214 | 0.5606 | 0.3858 | 0.0633 | 0.0625 | 151.7356 |
| Causally masked Transformer | 0.3763 | 0.5186 | 0.5567 | 0.3832 | 0.0367 | 0.0618 | 189.2282 |
| Recurrent state-space model | 0.5065 | 0.6165 | 0.6437 | 0.4921 | 0.4100 | 0.0651 | 3.8933 |

## External Recalibration

| Model | Horizon | Raw coverage | Recalibrated coverage | Raw width | Recalibrated width | Raw CRPS | Recalibrated CRPS | Raw Gaussian NLS | Recalibrated Gaussian NLS |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Probabilistic GRU-D-style model | 1 h | 0.8500 | 0.8987 | 1.4174 | 1.6969 | 0.2827 | 0.2881 | 0.7912 | 0.7617 |
| Probabilistic GRU-D-style model | 3 h | 0.8397 | 0.8847 | 1.5959 | 1.8538 | 0.3249 | 0.3286 | 0.9261 | 0.8991 |
| Probabilistic GRU-D-style model | 6 h | 0.8329 | 0.8975 | 1.7371 | 2.1546 | 0.3588 | 0.3652 | 1.0498 | 1.0162 |
| Probabilistic GRU-D-style model | 12 h | 0.8367 | 0.8872 | 1.8804 | 2.2129 | 0.3858 | 0.3902 | 1.1250 | 1.0942 |
| Probabilistic GRU-D-style model | 24 h | 0.8413 | 0.8825 | 2.0383 | 2.3265 | 0.4139 | 0.4175 | 1.2006 | 1.1737 |
| Causally masked Transformer | 1 h | 0.8524 | 0.8993 | 1.4280 | 1.7023 | 0.2823 | 0.2877 | 0.7790 | 0.7514 |
| Causally masked Transformer | 3 h | 0.8592 | 0.8814 | 1.7045 | 1.8414 | 0.3247 | 0.3269 | 0.8966 | 0.8886 |
| Causally masked Transformer | 6 h | 0.8537 | 0.8937 | 1.8688 | 2.1398 | 0.3564 | 0.3609 | 1.0135 | 1.0043 |
| Causally masked Transformer | 12 h | 0.8633 | 0.8894 | 2.0638 | 2.2589 | 0.3832 | 0.3864 | 1.0887 | 1.0842 |
| Causally masked Transformer | 24 h | 0.8704 | 0.8805 | 2.2751 | 2.3566 | 0.4123 | 0.4136 | 1.1843 | 1.1811 |
| Recurrent state-space model | 1 h | 0.5546 | 0.8887 | 0.9591 | 2.2335 | 0.3959 | 0.3850 | 2.4121 | 1.0702 |
| Recurrent state-space model | 3 h | 0.5184 | 0.8725 | 0.9734 | 2.3015 | 0.4371 | 0.4165 | 2.7513 | 1.1488 |
| Recurrent state-space model | 6 h | 0.4994 | 0.8774 | 0.9863 | 2.5129 | 0.4696 | 0.4452 | 3.0971 | 1.2167 |
| Recurrent state-space model | 12 h | 0.4900 | 0.8743 | 1.0014 | 2.5805 | 0.4921 | 0.4647 | 3.3187 | 1.2673 |
| Recurrent state-space model | 24 h | 0.4846 | 0.8769 | 1.0263 | 2.7198 | 0.5153 | 0.4855 | 3.6480 | 1.3359 |

The raw and recalibrated runs used identical split-specific Monte Carlo streams. Maximum patient-level NMAE difference was 4.768e-07; maximum mask-Brier difference was 0.000e+00.

## Frozen 12-Hour Paired NMAE Contrasts

| Split | Model A | Model B | A-B | 95% bootstrap interval | Patients |
| --- | --- | --- | ---: | ---: | ---: |
| internal_test | Probabilistic GRU-D-style model | Causally masked Transformer | 0.0009 | [-0.0013, 0.0032] | 1806 |
| internal_test | Probabilistic GRU-D-style model | Ridge vector autoregression | -0.0154 | [-0.0211, -0.0113] | 1806 |
| internal_test | Causally masked Transformer | Ridge vector autoregression | -0.0163 | [-0.0211, -0.0116] | 1806 |
| internal_test | Recurrent state-space model | Ridge vector autoregression | 0.0786 | [0.0733, 0.0842] | 1806 |
| internal_test | Ridge vector autoregression | Last observation carried forward | -0.0423 | [-0.0492, -0.0351] | 1806 |
| external_test | Probabilistic GRU-D-style model | Causally masked Transformer | 0.0028 | [0.0018, 0.0039] | 10178 |
| external_test | Probabilistic GRU-D-style model | Ridge vector autoregression | -0.0086 | [-0.0104, -0.0069] | 10178 |
| external_test | Causally masked Transformer | Ridge vector autoregression | -0.0114 | [-0.0138, -0.0095] | 10178 |
| external_test | Recurrent state-space model | Ridge vector autoregression | 0.0864 | [0.0839, 0.0888] | 10178 |
| external_test | Ridge vector autoregression | Last observation carried forward | -0.0452 | [-0.0489, -0.0413] | 10178 |

Negative contrast values favor model A. Intervals use a patient bootstrap after averaging the five fixed neural seeds. Across-seed variation is reported separately.

## Cross-Cohort 12-Hour NMAE Degradation

| Model | Internal | Zero-shot external | Absolute change [95% CI] | Relative change [95% CI] |
| --- | ---: | ---: | ---: | ---: |
| Last observation carried forward | 0.5525 | 0.5753 | 0.0228 [0.0081, 0.0342] | 4.1% [1.4%, 6.3%] |
| Global median | 0.6197 | 0.6634 | 0.0437 [0.0319, 0.0558] | 7.1% [5.1%, 9.2%] |
| Hourly median | 0.6180 | 0.6617 | 0.0437 [0.0322, 0.0559] | 7.1% [5.2%, 9.2%] |
| Ridge vector autoregression | 0.5102 | 0.5301 | 0.0198 [0.0093, 0.0269] | 3.9% [1.8%, 5.3%] |
| Probabilistic GRU-D-style model | 0.4949 | 0.5214 | 0.0265 [0.0174, 0.0346] | 5.4% [3.5%, 7.1%] |
| Causally masked Transformer | 0.4940 | 0.5186 | 0.0247 [0.0138, 0.0339] | 5.0% [2.7%, 7.0%] |
| Recurrent state-space model | 0.5889 | 0.6165 | 0.0276 [0.0199, 0.0376] | 4.7% [3.3%, 6.5%] |

## Rank Stability

| Type | Context | Comparison | Spearman mean [range] | Pairwise reversal mean [range] |
| --- | --- | --- | ---: | ---: |
| cross_horizon | external_test | 1h to 12h | 0.821 [0.821, 0.821] | 0.190 [0.190, 0.190] |
| cross_horizon | external_test | 1h to 24h | 0.821 [0.821, 0.821] | 0.190 [0.190, 0.190] |
| cross_horizon | internal_test | 1h to 12h | 0.893 [0.893, 0.893] | 0.095 [0.095, 0.095] |
| cross_horizon | internal_test | 1h to 24h | 0.857 [0.857, 0.857] | 0.143 [0.143, 0.143] |
| cross_site | 12h | internal_test to external_test | 1.000 [1.000, 1.000] | 0.000 [0.000, 0.000] |
| cross_site | 24h | internal_test to external_test | 0.964 [0.964, 0.964] | 0.048 [0.048, 0.048] |

## Training

| Model | Parameters | Best epoch, range | Validation loss, mean (SD) |
| --- | ---: | ---: | ---: |
| Probabilistic GRU-D-style model | 59,232 | 20-20 | 0.7326 (0.0000) |
| Recurrent state-space model | 93,320 | 20-20 | -1.5842 (0.0000) |
| Causally masked Transformer | 247,848 | 20-20 | 0.7153 (0.0000) |

Interpretation boundary: passive free-running forecasting only. The tables do not establish treatment effects, counterfactual validity, policy quality, clinical benefit, or deployment safety.
