# MedWM-Eval-ICU: Real-Data Evaluation Protocol

Status: dataset integrity and common-support baselines complete; five-seed neural matrix in progress  
Protocol date: 2026-09-12  
Amendment record: `protocol-deviations-and-amendments.md`  
Primary dataset: PhysioNet/Computing in Cardiology Challenge 2019 v1.0.0  
Dataset DOI: 10.13026/v64v-d857  
License: Creative Commons Attribution 4.0  
Data scale: 40,336 ICU subjects in two public hospital-system cohorts

## Central Research Question

Do model rankings and safety-relevant conclusions change when clinical dynamics models are evaluated by free-running rollout, probabilistic calibration, physiological validity, observation-process fidelity, and cross-site degradation rather than one-step prediction error alone?

## Scope

This study evaluates **passive clinical forecasting world models**. It does not claim treatment-effect estimation, counterfactual validity, or optimal clinical policy. The data contain hourly physiology and a sepsis label but do not expose a sufficiently complete action stream for causal intervention claims.

## Falsifiable Hypotheses

1. Models with similar one-step error will separate materially under 12- and 24-hour free-running rollout.
2. Calibration error and physiological constraint violations will increase with rollout horizon even when average point error remains acceptable.
3. Model rankings will be less stable under cross-hospital evaluation than within-hospital evaluation.
4. Training that exposes a model to its own prediction errors will improve rollout stability, but may not improve one-step accuracy.
5. Observation-mask prediction will reveal failures that value-only metrics miss because clinical measurement is informative rather than random.

Failure to observe these effects narrows or rejects the corresponding claim; it must not be rewritten as support.

## Dataset and Cohorts

The dataset provides one pipe-delimited hourly record per ICU subject with 34 time-varying vital-sign and laboratory variables, six demographic or administrative variables, and an hourly sepsis label.

- Cohort A: 20,336 subjects.
- Cohort B: 20,000 subjects.
- Main development: patient-level train/validation/internal-test split within cohort A.
- Cross-site test: cohort B, untouched during model and hyperparameter selection.
- Optional recalibration experiment: a protocol-defined small calibration
  partition from cohort B, evaluated on the remaining B subjects and reported
  separately from zero-shot transfer. The exact scalar procedure was fixed
  after the implementation seed, as recorded in the amendment log.

The downloaded v1.0.0 archive passed the prespecified structural audit:

- 20,336 cohort-A and 20,000 cohort-B patient files;
- 790,215 cohort-A and 761,995 cohort-B patient-hours;
- no invalid headers, malformed rows, nonmonotonic ICU-time sequences, or
  changing static fields;
- aggregate cohort fingerprints recorded in `results/dataset-audit.json`.

The deterministic patient split contains 14,247 training, 3,015 validation,
3,074 internal-test, 2,069 external-calibration, and 17,931 untouched
external-test subjects. Forecast-specific exclusions for insufficient context
or target availability are counted during each experiment.

## Prediction Task

Current manuscript scope: the teacher-forced multi-horizon comparison below is
superseded by the amendment record. The completed study uses a one-step
endpoint and free-running multi-hour rollout.

Given all observations, masks, and elapsed-time information available through hour \(t\), predict the joint distribution of future physiological observations and measurement masks.

- Minimum context: 12 observed ICU hours.
- Forecast horizons: 1, 3, 6, 12, and 24 hours where follow-up is available.
- Primary mode: autoregressive free-running rollout after the context window.
- Secondary mode: teacher-forced one-step prediction for comparison.
- Variables: all dynamic clinical variables that pass a preregistered coverage threshold in cohort-A training data; the threshold and retained list are frozen before model comparison.
- Targets: observed values and whether each variable is measured at each future hour.

## Preprocessing

1. Parse each subject independently and preserve patient boundaries.
2. Exclude `SepsisLabel` from model inputs for the physiology-forecasting task.
3. Fit all clipping, transformation, scaling, and coverage rules on cohort-A training data only.
4. Represent missingness with an observation mask and time since last measurement; do not interpret imputed values as observations.
5. Use robust scaling from the training cohort. Any log transforms must be fixed from variable semantics before outcome inspection.
6. Create deterministic patient-level splits and publish split identifiers or hashes.
7. Audit impossible source values separately from model-generated constraint violations.

## Baseline Matrix

| Baseline | Why included | Core configuration | Can run |
| --- | --- | --- | --- |
| Last observation carried forward | Strong clinical time-series sanity baseline | Per-variable persistence with training-cohort fallback | yes |
| Seasonal/hourly population baseline | Tests whether ICU-time priors explain performance | Training-cohort conditional median by ICU hour | yes |
| Ridge vector autoregression | Classical linear dynamics baseline | Three-lag robust-scaled VAR; regularization selected on 12-hour validation NMAE | yes; complete |
| GRU-D-style probabilistic forecaster | Established missingness-aware recurrent baseline | Gaussian value head plus mask head | implemented; five-seed run in progress |
| Causally masked Transformer forecaster | Strong sequence baseline | Autoregressive attention, Gaussian value head, mask head | implemented; five-seed run in progress |
| Recurrent state-space world model | Main model family | Stochastic latent transition, observation decoder, mask decoder | implemented; five-seed run in progress |

All neural models use the same context, targets, variable set, split,
preprocessing, maximum epoch count, optimizer settings, and early-stopping
criterion. Parameter counts are architecture specific and will be reported;
the comparison is not a parameter-matched mechanistic ablation.

## Main Experiments

### E1. Teacher-forced versus free-running evaluation

**Deferred in the current manuscript; retained here as original protocol
provenance.**

Compare every model at each horizon under teacher forcing and autoregressive rollout. Test whether one-step ranking predicts long-horizon ranking using Spearman correlation and paired patient-level bootstrap intervals.

### E2. Probabilistic calibration over horizon

Evaluate a moment-matched Gaussian negative log score, continuous ranked
probability score, interval coverage, interval width, and calibration error by
variable and horizon. The Gaussian score is a trajectory-sample summary, not
the exact likelihood of the rollout distribution. Report both marginal and
patient-macro averages.

### E3. Physiological validity

Measure:

- arterial-pressure ordering violations: systolic \(\ge\) mean \(\ge\) diastolic;
- bounded-variable violations, including oxygen saturation and fraction-inspired oxygen;
- implausible hourly changes using thresholds frozen from cohort-A training quantiles;
- multivariate state plausibility using a held-out density or conformity score fitted only on real cohort-A trajectories.

Constraint thresholds and their clinical rationale must be published.

### E4. Observation-process fidelity

Predict future measurement masks and report per-variable AUROC/AUPRC, Brier score, and calibration. Compare value scores conditioned on observed targets with joint value-mask likelihood to expose models that forecast common values but fail to reproduce clinically informative measurement patterns.

### E5. Cross-site degradation

Train and tune on cohort A, then evaluate unchanged on cohort B. Report absolute performance, relative degradation, calibration transfer, constraint violations, and subgroup results. Site adaptation or recalibration, if run, is a separate experiment.

### E6. Downstream trajectory utility

**Deferred in the current manuscript; retained here as original protocol
provenance.**

Train one frozen sepsis-risk probe on real cohort-A states only. Apply it to real and model-generated future trajectories. Test whether models preserve risk ordering and the official time-sensitive utility metric. This evaluates trajectory usefulness, not clinical treatment benefit.

## Mechanism Ablations

**Deferred in the current manuscript; retained here as original protocol
provenance.**

| Ablation | Mechanism tested | Primary affected evidence |
| --- | --- | --- |
| Teacher forcing only versus scheduled sampling | Exposure-bias contribution | rollout degradation |
| Remove multi-step rollout loss | Direct pressure for long-horizon stability | 6–24 h error and constraints |
| Deterministic versus stochastic latent state | Need for trajectory uncertainty | CRPS, coverage, NLL |
| Remove observation-mask decoder | Informative-missingness modeling | mask calibration and value bias |
| Remove time-since-last-measurement features | Irregular-observation handling | sparse-variable performance |
| Independent variable heads versus structured joint decoder | Multivariate consistency | pressure ordering and conformity |

## Statistics

- Five fixed random seeds for neural models; the implementation-seed chronology
  and exclusion sensitivity are recorded in the amendment log.
- Patient-level bootstrap confidence intervals for all primary comparisons.
- Paired tests on identical patient-horizon instances.
- Multiplicity control for the small set of preregistered primary hypotheses; other analyses are exploratory.
- Report effect sizes and confidence intervals, not only \(p\)-values.
- No test-set-driven hyperparameter selection.

## Primary Metrics

1. Normalized MAE at 12-hour free-running rollout.
2. CRPS at 12-hour free-running rollout.
3. Area under the rollout-degradation curve from 1 to 24 hours.
4. Empirical coverage error for nominal 90% intervals.
5. Physiological-constraint violations per 1,000 sampled rollout states.
6. Cross-site relative degradation from cohort A to cohort B.
7. Measurement-mask macro Brier score.

One-step error is secondary and cannot by itself support the central claim.

## Result Table Templates

### Main comparison

| Model | 1 h NMAE | 6 h NMAE | 12 h NMAE | 24 h NMAE | 12 h CRPS | 90% coverage error | Rollout-state pressure violations / 1,000 sampled states | Mask Brier |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| LOCF | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD |
| Hourly population | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD |
| Ridge VAR | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD |
| GRU-D | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD |
| Causally masked Transformer | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD |
| Recurrent state-space model | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD |

### Cross-site evaluation

| Model | A internal 12 h NMAE | B zero-shot 12 h NMAE | Relative degradation | A coverage error | B coverage error | A constraints | B constraints |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Each model | TBD | TBD | TBD | TBD | TBD | TBD | TBD |

### Ablations

| Variant | 1 h NMAE | 12 h NMAE | Rollout-degradation area | CRPS | Coverage error | Constraint violations |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Full model | TBD | TBD | TBD | TBD | TBD | TBD |
| Each ablation | TBD | TBD | TBD | TBD | TBD | TBD |

## Leakage and Integrity Checks

- No subject appears in more than one split.
- Scaling, clipping, coverage selection, and constraint thresholds use training data only.
- Forecast targets strictly follow the context cutoff.
- Repeated windows from one patient remain in the same split and are clustered in uncertainty estimates.
- Sepsis labels are excluded from world-model inputs.
- Cross-site cohort B is not used for model selection.
- Missing values are not scored as observed outcomes.
- Publication tables are generated only from frozen result files.

## Ethics and Claim Boundary

The data are deidentified and publicly available under CC BY 4.0. The study evaluates model behavior retrospectively. It does not validate clinical deployment, treatment recommendations, or prospective patient benefit.

## Execution Priority

1. Download and fingerprint the official dataset. **Complete.**
2. Build the deterministic parser, cohort audit, and split manifest. **Complete.**
3. Run LOCF and population baselines end to end. **Complete.**
4. Implement shared point-error, probabilistic, mask, and physiological-constraint tests. **Complete for the current primary outcomes.**
5. Run ridge VAR, then GRU-D, Transformer, and state-space models. **Ridge complete; first neural implementation seed complete and remaining matrix in progress.**
6. Freeze main results before ablations and downstream probe analysis.
7. Run integrity audit and independent scientific review before manuscript claims are finalized.

## No-Fabrication Status

The publication-support baseline report is frozen in
`results/sanity-baselines-common-support/report.md`. Neural results remain
developmental until all five seeds are complete and the aggregate tables are
frozen. Dataset and split counts above are verified local audit results.
Neither the baselines nor an individual neural seed establish the final
model-ranking result, causal effects, clinical benefit, or deployment validity.
