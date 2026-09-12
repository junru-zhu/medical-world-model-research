# Sanity-Baseline Evidence Report

Status: completed real-data sanity baselines; learned neural-model comparison not yet run

Dataset: PhysioNet/Computing in Cardiology Challenge 2019 v1.0.0

All models use cohort-A training statistics and the same deterministic patient split. Ridge hyperparameters were selected on the validation split. Cohort-B external test data were not used for selection.

## Patient-Macro NMAE

Values are mean patient NMAE with percentile 95% patient-level bootstrap intervals.

| Split | Model | 1 h | 12 h | 24 h |
| --- | --- | ---: | ---: | ---: |
| external_test | global_median | 0.6575 [0.6542, 0.6609] | 0.6645 [0.6603, 0.6685] | 0.6698 [0.6651, 0.6747] |
| external_test | hourly_median | 0.6611 [0.6579, 0.6645] | 0.6602 [0.6563, 0.6640] | 0.6617 [0.6569, 0.6666] |
| external_test | locf | 0.3897 [0.3879, 0.3915] | 0.5625 [0.5596, 0.5657] | 0.5981 [0.5939, 0.6024] |
| external_test | ridge_var | 0.3639 [0.3625, 0.3655] | 0.5228 [0.5198, 0.5257] | 0.5830 [0.5789, 0.5870] |
| internal_test | global_median | 0.6070 [0.5999, 0.6143] | 0.6217 [0.6135, 0.6300] | 0.6279 [0.6179, 0.6376] |
| internal_test | hourly_median | 0.6047 [0.5975, 0.6122] | 0.6163 [0.6087, 0.6243] | 0.6220 [0.6126, 0.6318] |
| internal_test | locf | 0.3759 [0.3722, 0.3798] | 0.5431 [0.5368, 0.5494] | 0.5907 [0.5818, 0.6002] |
| internal_test | ridge_var | 0.3500 [0.3467, 0.3534] | 0.5018 [0.4957, 0.5076] | 0.5580 [0.5504, 0.5668] |

## Arterial-Pressure Ordering Violations

Violations per 1,000 generated states for systolic >= mean >= diastolic pressure.

| Split | Model | 1 h | 12 h | 24 h |
| --- | --- | ---: | ---: | ---: |
| external_test | global_median | 0.000 | 0.000 | 0.000 |
| external_test | hourly_median | 0.000 | 0.000 | 0.000 |
| external_test | locf | 4.953 | 4.750 | 4.794 |
| external_test | ridge_var | 2.501 | 0.509 | 0.097 |
| internal_test | global_median | 0.000 | 0.000 | 0.000 |
| internal_test | hourly_median | 0.000 | 0.000 | 0.000 |
| internal_test | locf | 50.711 | 46.906 | 43.133 |
| internal_test | ridge_var | 25.306 | 2.208 | 0.000 |

## Bounded Interpretation

- Ridge VAR has lower NMAE than LOCF and both population baselines at every tested horizon and in both test cohorts.
- NMAE increases with horizon for the learned and persistence baselines, demonstrating rollout degradation even in this point-forecast setting.
- All models degrade on the external cohort in NMAE, but the magnitude is model- and horizon-dependent.
- Population medians have zero pressure-ordering violations by construction while having worse forecast error. A zero constraint count is therefore not evidence of useful dynamics.
- Ridge constraint violations decline with horizon as its forecasts revert toward common population states; this may reflect mean collapse rather than physiological preservation.
- The model ranking is stable across these four sanity baselines. The ranking-change hypothesis remains untested until stronger probabilistic sequence models are evaluated.
- These point models do not evaluate calibration, stochastic trajectory diversity, observation-mask fidelity, causal effects, or clinical benefit.
