# Study-Level Extraction Schema

Status: Draft schema for dual coding

## Identification

| Field | Coding rule |
| --- | --- |
| Study ID | Stable citation key |
| Title | Publication title |
| Authors | Full metadata |
| First-public date | Earliest public version |
| Current version | Version inspected |
| Status | Peer reviewed / workshop / preprint |
| Domain | EHR / physiology / oncology imaging / ultrasound / surgery / other |
| Primary source | Stable proceedings, DOI, or arXiv URL |

## Data and Setting

| Field | Coding rule |
| --- | --- |
| Dataset or cohort | Name and version where reported |
| Sample scale | Patients, encounters, videos, images, procedures, or episodes |
| Institution count | Number and geographic setting |
| Split | Patient, temporal, institutional, or random |
| Observation process | Regular / irregular; modality and sampling |
| Missingness | Handling and whether missingness is modeled |
| Censoring or competing events | Discharge, death, dropout, truncation, or not applicable |

## World-Model Definition

| Field | Coding rule |
| --- | --- |
| State | Explicit or latent state and included variables |
| Observation decoder | Future event, scalar, image, video, or other output |
| Action | Treatment, dose, event, motion, robot command, text, or absent |
| Action provenance | Intended, ordered, administered, observed behavior, or simulated |
| Transition mechanism | Autoregressive, latent transition, diffusion, video dynamics, or other |
| Horizon | One-step and maximum reported rollout |
| Rollout regime | Teacher forced / free running / closed loop |
| Capability claim | Forecasting / action conditioned / counterfactual / planning |

## Evaluation

| Field | Coding rule |
| --- | --- |
| Baselines | Strongest relevant baselines and action-agnostic baseline |
| State-fidelity metrics | Metrics and clinically meaningful strata |
| Transition metrics | Horizon-specific or trajectory-level metrics |
| Rollout-stability metrics | Drift, divergence, constraint violations, or not reported |
| Action-sensitivity tests | Removal, shuffling, perturbation, dose/timing, or not reported |
| Calibration and uncertainty | Metric, horizon, subgroup, and abstention use |
| External validation | Institution, time, geography, device, or population |
| Decision utility | Clinician, policy, navigation, control, or downstream task |
| Safety evaluation | Hazard, severity, constraint, override, and monitoring |
| Statistical analysis | Confidence intervals, resampling, significance, or not reported |

## Causal Interpretation

| Field | Coding rule |
| --- | --- |
| Causal language used | Exact capability language |
| Estimand | Observed-policy prediction / population intervention effect / regime value / individual trajectory / none |
| Eligibility and time zero | Explicit / partial / absent |
| Treatment strategies | Defined / partial / absent |
| Confounding strategy | Design or adjustment |
| Positivity and overlap | Evaluated / discussed / absent |
| Censoring strategy | Defined / partial / absent |
| Counterfactual validation | Randomized, quasi-experimental, target trial, negative control, domain constraint, or none |
| Supported interpretation | Reviewer-coded evidence boundary |

## Reproducibility and Access

| Field | Coding rule |
| --- | --- |
| Code | Public / planned / unavailable / unclear |
| Model weights | Public / planned / unavailable / unclear |
| Data | Public / credentialed / request-based / private |
| Preprocessing | Reproducible / partial / insufficient |
| Randomness | Seeds or repeated runs reported |
| License and terms | Verified source and date |

## Coding Values

For binary reporting features:

- `2`: reported with enough detail to reproduce or audit;
- `1`: reported partially;
- `0`: not reported in inspected text;
- `NA`: not applicable to the study claim;
- `NI`: not yet inspected.

Every `0`, `1`, or `2` should carry a page, section, table, appendix, or stable-source anchor.

