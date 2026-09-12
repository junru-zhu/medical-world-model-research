# Preliminary Dataset Task Cards

Status: Preliminary review artifact  
Scoring: 0 = weak or absent, 1 = partial, 2 = strong  
Purpose: Match datasets to permissible medical-world-model claims; scores are not dataset quality rankings

## Criteria

| Criterion | 0 | 1 | 2 |
| --- | --- | --- | --- |
| Action observability | No meaningful action stream | Recorded or proxy action with ambiguity | Explicit delivered action with timing and magnitude |
| Temporal density | Sparse isolated records | Irregular or moderate longitudinal density | Dense repeated state and action measurement |
| External-validation utility | Same role as development data | Partial population or device shift | Distinct institution or multicenter deployment-like shift |
| Causal support | Observational with no counterfactual support | Some design leverage or known response constraints | Randomized or strong quasi-experimental intervention evidence |
| Access reproducibility | Private or terms unclear | Credentialed, request-based, or DUA | Public with stable version and direct download |

## Summary Matrix

| Dataset | Action | Density | External utility | Causal support | Access | Best-supported use |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| MIMIC-IV v3.1 | 1 | 2 | 0 | 0 | 1 | Development of ICU/ED forecasting and observed-policy rollout |
| eICU-CRD v2.0 | 1 | 2 | 2 | 0 | 1 | Multicenter external validation of an ICU model developed elsewhere |
| HiRID v1.1.1 | 1 | 2 | 1 | 0 | 1 | High-frequency physiological rollout and short-horizon intervention response |
| OhioT1DM | 2 | 2 | 0 | 0 | 1 | Explicit insulin-, meal-, and activity-conditioned glucose dynamics |
| MIMIC-CXR-JPG v2.1.0 | 0 | 1 | 1 | 0 | 1 | Longitudinal image-state prediction linked to clinical records |
| EchoNet-Dynamic | 0 | 2 | 1 | 0 | 2 | Passive cardiac-video state and dynamics representation |
| Cholec80 | 1 | 2 | 0 | 0 | 1 | Surgical video dynamics and action-proxy recognition |

## MIMIC-IV v3.1

- **State:** ICU and emergency observations, laboratory measurements, diagnoses, medications, procedures, and charted events.
- **Action provenance:** Orders, administrations, procedures, and recorded care events. Intent, adherence, overlap, and clinician policy remain confounded.
- **Temporal structure:** Dense but irregular; missingness and measurement timing are informative.
- **Censoring:** Discharge, transfer, and death must be modeled explicitly.
- **Permissible claims:** Forecasting under observed care; associational action-conditioned rollout.
- **Unsupported claim without extra design:** Patient-specific treatment benefit under alternative interventions.
- **Benchmark role:** Development cohort.
- **Access:** PhysioNet credentialing, training, and data-use agreement.

## eICU-CRD v2.0

- **State:** Multicenter ICU records with site-dependent interfaces and documentation.
- **Action provenance:** Recorded treatments and procedures with observational confounding.
- **Temporal structure:** Dense ICU trajectories; site-specific missingness is part of the shift.
- **Permissible claims:** Frozen external validation, calibration transfer, site heterogeneity, and subgroup degradation.
- **Unsupported claim without extra design:** Causal comparison of treatment strategies.
- **Benchmark role:** External validation for a model developed on MIMIC-IV or another institution.
- **Access:** PhysioNet credentialing and data-use agreement.

## HiRID v1.1.1

- **State:** High-frequency ICU measurements and treatment events.
- **Action provenance:** Recorded clinical treatment events; intent and confounding remain unresolved.
- **Temporal structure:** Strong fit for short- and medium-horizon free-running physiology.
- **Permissible claims:** Dense state-transition forecasting, horizon degradation, calibration, and clinically constrained rollout.
- **Unsupported claim without extra design:** Individual counterfactual treatment effect.
- **Benchmark role:** Temporal-resolution stress test and cross-cohort validation.
- **Access:** Contributor-reviewed PhysioNet access.

## OhioT1DM

- **State:** Continuous glucose, insulin, meals, exercise, sleep, stress, and wearable measurements.
- **Action provenance:** Insulin dosing and recorded behavioral events have clearer semantics than generic EHR treatment tokens.
- **Temporal structure:** Eight weeks for each of twelve participants.
- **Permissible claims:** Action-conditioned glucose forecasting, action sensitivity, hypoglycemia-risk prediction, and within-person rollout.
- **Unsupported claim without extra design:** Broad population generalization or causal comparison of arbitrary insulin policies.
- **Benchmark role:** Low-scale task with explicit actions and clinically meaningful constraints.
- **Access:** Data-use agreement required.

## MIMIC-CXR-JPG v2.1.0

- **State:** Chest radiographs with structured labels and linkage to MIMIC clinical records.
- **Action provenance:** No direct image-acquisition or treatment-action stream in the standard dataset.
- **Temporal structure:** Serial images exist but are sparse and care-dependent.
- **Permissible claims:** Passive longitudinal image-state prediction and consistency with EHR events.
- **Unsupported claim without extra design:** Treatment-conditioned radiographic counterfactuals.
- **Benchmark role:** Imaging track for observation and trajectory validity.
- **Access:** PhysioNet credentialing and data-use agreement.

## EchoNet-Dynamic

- **State:** Apical four-chamber echocardiography videos with ventricular labels and outcomes.
- **Action provenance:** The public dataset does not provide probe-motion actions.
- **Temporal structure:** Dense within-video cardiac cycles, limited longitudinal care trajectory.
- **Permissible claims:** Passive video dynamics, cardiac representation, and state estimation.
- **Unsupported claim:** Probe-guidance or action-conditioned acquisition without another motion dataset.
- **Benchmark role:** Video-dynamics pretraining or passive evaluation.
- **Access:** Stable public download under current dataset terms.

## Cholec80

- **State:** Laparoscopic cholecystectomy videos with phase and tool-presence annotations.
- **Action provenance:** Tool visibility and motion are action proxies, not complete robot commands or tissue-force measurements.
- **Temporal structure:** Dense video with procedural phases.
- **Permissible claims:** Surgical visual dynamics, phase progression, tool-action recognition, and conditional video generation.
- **Unsupported claim without extra data:** Physical tissue response, robot safety, or executable action planning.
- **Benchmark role:** Visual-dynamics track.
- **Access:** Current authoritative access and redistribution terms require final verification.

## Original-Paper Implication

The strongest benchmark design is a multi-track study rather than a single universal score:

1. **Longitudinal clinical track:** MIMIC-IV development with eICU frozen external validation.
2. **Explicit-action track:** OhioT1DM for action sensitivity and calibrated glucose rollout.
3. **Embodied or visual track:** deferred unless probe-motion or robot-action data are available.

The final choice depends on verified data access and compute. No dataset in this set provides observed outcomes for every alternative intervention on the same patient.
