# Experiment Protocol Deviations and Amendments

Record date: 2026-09-12

This record preserves the chronology between the initial broad experiment
protocol and the narrower manuscript analysis. It does not overwrite the
original protocol.

| Item | Timing | Classification | Rationale and consequence |
| --- | --- | --- | --- |
| Common 24-hour support | Identified after deterministic and ridge implementation, before the final comparative analysis | Corrective amendment | Early baseline outputs used horizon-specific stride-1 anchors, whereas neural evaluation used 24-hour-eligible stride-6 anchors. Publication comparisons were rerun on the same 24-hour-eligible anchors at every horizon. Superseded outputs remain developmental and are not used in the manuscript. |
| Frozen cohort-B calibration partition | Fixed before external recalibration analysis | Protocol operationalization | Cohort B was divided into 2,069 external-calibration and 17,931 external-test patients. Only horizon-wise spread multipliers are fitted on the calibration partition. Zero-shot and recalibrated external-test results are reported separately. |
| First neural implementation seed | Completed before the remaining seed matrix | Pipeline pilot | Seed 20260912 verified training, free-running evaluation, calibration fitting, and result serialization. The five-seed list, common support, primary outcomes, and remaining execution matrix were then frozen. The pilot seed remains in the reported five-seed set; this chronology is disclosed. |
| Stochastic-model calibration question | Formalized after inspection of the implementation seed and before remaining seeds | Exploratory analysis | Whether the recurrent state-space model is better calibrated than simpler probabilistic forecasters is reported as exploratory, not as a protocol-defined hypothesis. Negative results are retained. |
| Scheduled-sampling hypothesis and ablation | Not implemented before the main result freeze | Deferred | The initial protocol's exposure-bias intervention is outside the current equal-budget model comparison. The manuscript does not claim that a training intervention improves rollout stability. |
| Teacher-forced multi-horizon comparison | Not implemented before the main result freeze | Deferred | The one-hour endpoint is a single generated step from real history; all longer endpoints use free-running rollout. The manuscript does not claim a matched teacher-forced-versus-free-running contrast at each horizon. |
| Additional physiological change thresholds and conformity score | Not implemented before the main result freeze | Deferred secondary analysis | The current primary safety outcome is a set of explicit physiological bounds and arterial-pressure ordering checks. No broader physiological-validity claim is made. |
| Downstream sepsis-risk probe | Not implemented before the main result freeze | Deferred secondary analysis | The paper is restricted to passive physiological and observation-mask forecasting and makes no downstream clinical-utility claim. |
| Mechanism ablations and subgroup analysis | Not implemented before the main result freeze | Deferred follow-up | The present study compares model families under a shared training schedule. Mechanistic attribution and subgroup performance require separate analyses. |
| Architecture size | Confirmed during implementation audit before final result freeze | Reporting clarification | Hidden size, training schedule, optimizer settings, and stopping rules are shared, but parameter counts differ by architecture. Results are model-family comparisons and cannot isolate the effect of recurrence, attention, stochastic state, or parameter count. |
| Inferential contrasts | Fixed after the implementation seed and before remaining seeds | Statistical clarification | The initial protocol proposed multiplicity control but did not define exact null contrasts. The final analysis averages the five fixed seed instances, resamples patients for a frozen set of 12-hour NMAE comparisons, reports seed variation separately, and does not present retrospectively specified p-values as confirmatory tests. |
| Monte Carlo stream alignment for recalibration | Identified during first-seed artifact audit, before final result freeze | Corrective amendment | The initial raw run evaluated internal then external data, whereas the recalibrated run evaluated external data alone; sequential random-number consumption therefore produced different external trajectories even though spread scaling preserves the sample mean. Evaluation now resets a deterministic split-specific random stream, affected artifacts are regenerated, and the frozen analyzer requires patient-level point-error and mask-prediction invariance. |
| Physiological-constraint state | Identified during first-seed artifact audit, before final result freeze | Corrective amendment | Initial constraint counts used all decoder emissions, including values masked as unobserved and not fed back into the rollout. The primary metric now evaluates the actual carried-forward rollout state after the sampled mask update; decoder-emission violations remain a separately labeled diagnostic. Affected artifacts are regenerated. |
| Evaluation batch size | Fixed during corrected-pipeline runtime audit, before final result freeze | Computational implementation | Training remains at batch size 64 for every seed. Evaluation uses batch size 128 to reduce accelerator-kernel overhead. Evaluation batching changes only Monte Carlo draw ordering within the frozen random stream and does not alter support, model parameters, or metric definitions. |

## Confirmatory and exploratory distinction

The manuscript's protocol-defined questions correspond to the original protocol's
one-step versus long-horizon separation, horizon-dependent calibration and
physiological behavior, cross-cohort degradation, and observation-mask
fidelity. The stochastic latent-model comparison is exploratory. The original
scheduled-sampling hypothesis is untested.

## Claim boundary

All current analyses concern passive forecasting under the observed
measurement process. They do not identify treatment effects, counterfactual
outcomes, optimal policies, prospective clinical benefit, or deployment
safety.
