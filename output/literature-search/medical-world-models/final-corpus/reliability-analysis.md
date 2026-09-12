# MedWM-Eval Coding Reliability

Records: 85; study-field decisions: 1785; overall raw agreement: 88.0%.

Intervals are percentile 95% confidence intervals from a study-level bootstrap with 2,000 replicates and seed 20260912.

| Field | Raw agreement | Cohen kappa (95% CI) | Linear weighted kappa (95% CI) |
| --- | ---: | ---: | ---: |
| highest capability claim | 88.2% | 0.835 (0.732 to 0.931) | NA |
| state evidence | 94.1% | 0.780 (0.576 to 0.946) | 0.780 (0.551 to 0.935) |
| dynamics evidence | 78.8% | 0.603 (0.417 to 0.754) | 0.652 (0.477 to 0.790) |
| rollout evidence | 87.1% | 0.806 (0.694 to 0.911) | 0.853 (0.759 to 0.931) |
| action evidence | 74.1% | 0.598 (0.456 to 0.736) | 0.556 (0.381 to 0.710) |
| uncertainty evidence | 87.1% | 0.762 (0.621 to 0.885) | 0.785 (0.654 to 0.892) |
| causal evidence | 83.5% | 0.703 (0.563 to 0.832) | 0.545 (0.226 to 0.810) |
| external evidence | 90.6% | 0.849 (0.737 to 0.940) | 0.875 (0.786 to 0.951) |
| decision evidence | 90.6% | 0.855 (0.755 to 0.944) | 0.884 (0.796 to 0.954) |
| safety evidence | 84.7% | 0.724 (0.569 to 0.850) | 0.766 (0.640 to 0.878) |
| reproducibility evidence | 78.8% | 0.669 (0.518 to 0.800) | 0.728 (0.602 to 0.832) |
| free running rollout | 94.1% | 0.871 (0.748 to 0.974) | NA |
| horizon resolved results | 89.4% | 0.791 (0.647 to 0.906) | NA |
| formal calibration | 97.6% | 0.789 (0.317 to 1.000) | NA |
| frozen external validation | 87.1% | 0.678 (0.485 to 0.834) | NA |
| action agnostic comparator | 85.9% | 0.754 (0.606 to 0.873) | NA |
| action perturbation | 88.2% | 0.799 (0.670 to 0.904) | NA |
| explicit causal estimand | 89.4% | 0.808 (0.685 to 0.918) | NA |
| closed loop evaluation | 87.1% | 0.817 (0.713 to 0.914) | NA |
| safety hazard test | 95.3% | 0.859 (0.693 to 0.969) | NA |
| public code | 96.5% | 0.946 (0.874 to 1.000) | NA |

These statistics characterize reproducibility between the two developmental AI-assisted coding passes. They do not validate MedWM-Eval and do not replace human dual coding.
