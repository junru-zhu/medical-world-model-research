# Provisional Gap Implications from the Sampled-Audit Additions

Status date: 2026-09-12  
Status: developmental inference only; do not cite as a final review result  
Evidence base: five provisional empirical additions with two independent
source-grounded extraction and MedWM-Eval coding passes, followed by
source-grounded adjudication

The two MedWM-Eval passes agreed on 91 of 105 coded decisions (86.67%).
Fourteen disagreements across four studies were adjudicated while preserving
both reviewers' anchors and the reason for each final decision.

## Study-Level Implications

| Study | Evidence added to the map | Important boundary |
| --- | --- | --- |
| Clin-JEPA | Free-running 48-hour latent EHR rollout with horizon-resolved drift and public implementation | One database; no decoded physiological trajectory, action perturbation, calibration, external validation, causal identification, or decision evaluation |
| DRIFT | Multihorizon ICU physiology, explicit action-path replacement, paired inference, and independently trained eICU replication | Action audit measures input dependence rather than counterfactual validity; external evidence requires retraining and is not site-held-out; no calibration or clinical utility |
| Ultrasound-driven autonomous microrobots | Real closed-loop control, simulation-to-physical transfer, unseen-channel adaptation, explicit failure/recovery tests, and public artifacts | Artificial vascular platform rather than in-vivo or clinical validation; no direct transition-fidelity or calibrated-uncertainty evaluation |
| Surgical visual-trajectory model | Fully autoregressive 15-step visual and instrument-motion forecasting with horizon-resolved degradation | No exogenous action, executable planning, external dataset, calibration, strong architecture comparator, or safety evaluation |
| Chreode | Large-scale pretrained cellular transition representation with held-out developmental, fate, and perturbation tasks | One-step rather than recursive rollout; action input is null during temporal pretraining; downstream fine-tuning or GEARS reuse; no calibrated uncertainty, adult-human validation, wet-lab intervention test, or causal identification |

## Provisional Synthesis

These additions broaden the strongest evidence in three directions:

1. **Long-horizon latent rollout:** Clin-JEPA directly measures 48-hour
   autoregressive drift while conditioning on observed hourly action
   embeddings.
2. **Action sensitivity without causal interpretation:** DRIFT performs an
   unusually explicit action-path audit while stating that altered-path results
   are not valid counterfactual outcomes.
3. **Embodied closed-loop evaluation:** the microrobot study demonstrates real
   control with recovery and stress testing on an artificial platform.

They do not supply the combination that remains most relevant to the planned
real-data study:

- decoded, clinically meaningful multivariate trajectories;
- free-running or recursively updated long-horizon prediction;
- formal calibration or interval coverage by horizon;
- frozen institutional or population shift;
- action semantics that are not overinterpreted as causal effects; and
- a reproducible comparison against simple observed-data baselines.

Across all five additions, none reports formal predictive calibration. Only
one has frozen external validation, and that evidence applies to a zero-shot
cell-fate task rather than a clinical trajectory rollout. The leading benchmark
gap therefore remains a **calibrated, horizon-resolved evaluation of clinical
trajectory models under external distribution shift**.
The wording should remain provisional until the expanded-search and exhaustive
rescreen tracks are adjudicated and all novel empirical studies are
independently extracted and coded.

## Consequence for the Original Study

The current PhysioNet Challenge 2019 design still targets the defensible core
of the gap:

- multistep physiological forecasting at 1, 12, and 24 hours;
- internal versus externally separated cohorts;
- strong simple baselines, including last observation carried forward and
  regularized linear prediction;
- calibration and coverage analyses added before any world-model claim; and
- no causal or treatment-effect interpretation.

The experiment should not be described as establishing a clinical world model
until it also evaluates iterative rollout behavior, joint-state coherence,
missingness and censoring, uncertainty under shift, and reproducibility across
seeds and preprocessing choices.
