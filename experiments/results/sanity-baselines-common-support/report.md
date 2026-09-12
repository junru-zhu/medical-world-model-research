# Sanity-Baseline Evidence Report

Status: completed real-data sanity-baseline component; probabilistic neural results are stored and summarized separately

Dataset: PhysioNet/Computing in Cardiology Challenge 2019 v1.0.0

All models use cohort-A training statistics and the same deterministic patient split. Ridge hyperparameters were selected on the validation split. Cohort-B external test data were not used for selection.

## Patient-Macro NMAE

Values are mean patient NMAE with percentile 95% patient-level bootstrap intervals.

| Split | Model | 1 h | 12 h | 24 h |
| --- | --- | ---: | ---: | ---: |
| external_test | global_median | 0.6634 [0.6582, 0.6689] | 0.6634 [0.6577, 0.6690] | 0.6698 [0.6640, 0.6753] |
| external_test | hourly_median | 0.6699 [0.6642, 0.6757] | 0.6617 [0.6562, 0.6669] | 0.6624 [0.6571, 0.6680] |
| external_test | locf | 0.3853 [0.3815, 0.3895] | 0.5753 [0.5706, 0.5803] | 0.6033 [0.5980, 0.6089] |
| external_test | ridge_var | 0.3610 [0.3575, 0.3645] | 0.5301 [0.5257, 0.5343] | 0.5862 [0.5813, 0.5909] |
| internal_test | global_median | 0.6100 [0.5988, 0.6208] | 0.6197 [0.6085, 0.6307] | 0.6294 [0.6183, 0.6406] |
| internal_test | hourly_median | 0.6097 [0.5993, 0.6202] | 0.6180 [0.6076, 0.6289] | 0.6235 [0.6120, 0.6352] |
| internal_test | locf | 0.3657 [0.3577, 0.3739] | 0.5525 [0.5420, 0.5631] | 0.5998 [0.5877, 0.6122] |
| internal_test | ridge_var | 0.3417 [0.3344, 0.3493] | 0.5102 [0.5019, 0.5190] | 0.5664 [0.5560, 0.5769] |

## Arterial-Pressure Ordering Violations

Violations per 1,000 generated states for systolic >= mean >= diastolic pressure.

| Split | Model | 1 h | 12 h | 24 h |
| --- | --- | ---: | ---: | ---: |
| external_test | global_median | 0.000 | 0.000 | 0.000 |
| external_test | hourly_median | 0.000 | 0.000 | 0.000 |
| external_test | locf | 5.320 | 5.320 | 5.320 |
| external_test | ridge_var | 3.021 | 0.624 | 0.131 |
| internal_test | global_median | 0.000 | 0.000 | 0.000 |
| internal_test | hourly_median | 0.000 | 0.000 | 0.000 |
| internal_test | locf | 44.915 | 44.915 | 44.915 |
| internal_test | ridge_var | 19.638 | 0.583 | 0.000 |

## Bounded Interpretation

- Ridge VAR has lower NMAE than LOCF and both population baselines at every tested horizon and in both test cohorts.
- NMAE increases with horizon for the learned and persistence baselines, demonstrating rollout degradation even in this point-forecast setting.
- All models degrade on the external cohort in NMAE, but the magnitude is model- and horizon-dependent.
- Population medians have zero pressure-ordering violations by construction while having worse forecast error. A zero constraint count is therefore not evidence of useful dynamics.
- Ridge constraint violations decline with horizon as its forecasts revert toward common population states; this may reflect mean collapse rather than physiological preservation.
- The model ranking is stable across these four sanity baselines. This statement is restricted to the deterministic and ridge comparison; the publication analysis adds probabilistic neural models on the same support.
- These point models do not evaluate calibration, stochastic trajectory diversity, observation-mask fidelity, causal effects, or clinical benefit.
