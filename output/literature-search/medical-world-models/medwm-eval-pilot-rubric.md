# MedWM-Eval Pilot Coding Rubric

Status: developmental dual-coding instrument  
Unit of analysis: one empirical study  
Evidence source: primary paper plus available appendix or official proceedings

## General Rule

Code against the highest capability claim made in the title, abstract,
introduction, results, or conclusion. A lower-capability experiment does not
support a higher-capability claim. `0` means the relevant evidence was not
reported in the inspected primary text; it does not prove the work was not
performed. `NI` means the primary evidence could not be inspected.

## Highest Capability Claim

- `passive_forecasting`: predicts future state or observation under the
  observed process.
- `action_conditioned`: changes a rollout according to a defined action but
  does not make an identified alternative-treatment claim.
- `counterfactual`: compares outcomes under alternative interventions or uses
  causal/counterfactual language for unobserved outcomes.
- `planning`: selects or optimizes sequential actions through model rollout.

## Ordinal Evidence Domains

Use `0`, `1`, `2`, or `NA`.

| Field | 0 | 1 | 2 |
| --- | --- | --- | --- |
| State evidence | Clinically/task-relevant state not evaluated | Indirect proxy or narrow component | Intended state variables or task-relevant latent state evaluated directly |
| Dynamics evidence | Static/downstream evaluation only | One-step transition or indirect temporal evidence | Direct trajectory/transition evaluation at the claimed operating regime |
| Rollout evidence | No free-running or closed-loop fidelity test | Recursive/closed-loop use without horizon-resolved fidelity | Free-running multi-step fidelity, degradation, or stability measured across meaningful horizons |
| Action evidence | Claimed action use not tested | Action conditioning or limited ablation | Action-agnostic comparator plus removal, shuffle, timing, dose, or in-support perturbation |
| Uncertainty evidence | No predictive uncertainty evaluation | Samples, variance, Brier/NLL, or uncertainty proxy without calibration/coverage | Calibration or interval coverage assessed, preferably by horizon or shift |
| Causal evidence | Counterfactual claim rests on conditioning or policy correlation | Partial adjustment, OPE, sensitivity, or causal discussion without complete identification | Explicit estimand, time zero, strategies, confounding/censoring/overlap assumptions, and counterfactual validation |
| External evidence | Internal/random/same-source evaluation only | Adapted second cohort, limited domain transfer, or simulated-to-real proxy | Frozen temporal, institutional, geographic, device, or population validation |
| Decision evidence | No decision or control evaluation | Offline proxy, treatment overlap, downstream probe, or retrospective preference | Closed-loop task, clinician decision, policy value, or workflow utility against a relevant comparator |
| Safety evidence | No hazard or safety test | Constraint proxy, limited failure analysis, or qualitative safety discussion | Defined hazards with severity, stress/failure tests, constraints, recovery/override, or subgroup worst cases |
| Reproducibility evidence | Essential implementation and data path unavailable | Partial code/data/configuration or governed data with incomplete pipeline | Inspectable code plus sufficient data/preprocessing/configuration to reproduce the main evaluation |

For `causal_evidence`, use `NA` when the study does not make a counterfactual,
treatment-effect, or alternative-policy claim. For `action_evidence`, use `NA`
when the model is strictly passive. Other domains ordinarily use `0` rather
than `NA` when relevant evidence is absent.

## Descriptive Feature Codes

| Field | Allowed values | Rule |
| --- | --- | --- |
| Free-running rollout | `yes`, `no`, `unclear` | `yes` only when the model consumes its own generated state/observation or is evaluated in a closed loop |
| Horizon-resolved results | `yes`, `no`, `unclear` | Performance or failure reported at two or more meaningful rollout horizons |
| Formal calibration | `yes`, `no`, `unclear` | Reliability, ECE, calibration slope/intercept, or interval-coverage calibration; Brier/NLL alone is `no` |
| Frozen external validation | `yes`, `no`, `unclear` | No fitting, fine-tuning, or hyperparameter selection on the external test cohort |
| Action-agnostic comparator | `yes`, `no`, `NA`, `unclear` | Comparator removes or ignores the claimed action |
| Action perturbation | `yes`, `no`, `NA`, `unclear` | Removal, shuffle, timing, dose, magnitude, or other defined action sensitivity |
| Explicit causal estimand | `yes`, `no`, `NA`, `unclear` | A population/individual intervention contrast or policy value is mathematically or textually defined |
| Closed-loop evaluation | `real`, `simulation`, `offline`, `no`, `unclear` | Code the strongest demonstrated setting |
| Safety hazard test | `yes`, `no`, `unclear` | An explicit clinical/physical hazard, constraint violation, failure, or recovery test |
| Public code | `yes`, `no`, `unclear` | Inspectable implementation at coding cutoff |

## Anchoring and Confidence

- `evidence_anchors` must name the page, section, table, figure, appendix, or
  stable official source supporting the codes.
- `reviewer_notes` should explain any code likely to be disputed.
- `confidence` is `high`, `medium`, or `low`.

The pilot domains are not summed into one overall score.
