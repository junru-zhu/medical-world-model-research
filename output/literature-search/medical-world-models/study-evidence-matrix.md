# Full-Text Evidence Matrix: Empirical Medical World Models

Extraction date: 2026-09-12  
Corpus: 12 empirical studies  
Coverage: Primary paper and available appendix or supplement inspected for every study  
Codes: `NR` = not reported in inspected text; `NI` = claimed resource not inspectable or locatable

## Quantitative Audit

| Evaluation feature | Count | Interpretation |
| --- | ---: | --- |
| Formal calibration error reported | 1/12 | The postoperative cardiology model reports ECE; CLARITY reports Brier score without reliability or coverage analysis |
| Meaningful external cohort evaluation | 3/12 | HealthFormer, CLARITY, and Brain-WM |
| Adapted public-cohort evaluation | 1/12 | MeWM fine-tunes or validates on 80% of the public cohort before testing |
| Identified causal treatment effect | 0/12 | No study states and identifies a patient-specific or population treatment-effect estimand |
| Executable action evaluated in closed loop | 1/12 | Surgical WAM, entirely in simulation |
| Inspectable public code at extraction time | 5/12 | MeWM, CLARITY, postoperative cardiology, Brain-WM, and EchoWorld |
| Uncertainty growth across rollout horizon | 0/12 | No study evaluates calibrated uncertainty growth over repeated rollout |

## Longitudinal, Physiology, and Treatment-Conditioned Studies

| Study | Status and data | State and action | Rollout | Main evidence | Calibration and external validation | Causal and reproducibility boundary |
| --- | --- | --- | --- | --- | --- | --- |
| EHRWorld [5] | arXiv v1; MIMIC-IV-derived EHRWorld-110K with 110,513 hospitalizations and about 17.5M events | Timestamp, demographics, discharge-derived diagnosis context, event history; inquiries plus observed medications and procedures | Teacher-forced next step and autoregressive admission-to-discharge rollout | Set similarity, SMAPE, clinical-status F1, categorical metrics, retention, high-sensitivity degradation, latency | Calibration NR; external validation NR | Chronological conditioning, not treatment-effect identification; code and derived dataset release NR |
| HealthFormer [6] | arXiv v1; HPP 15,319 participants, with external cohorts from UK Biobank, NHANES, Framingham, and PNP3 | Tokenized physiology, medications, behavior, age, sex, and time; edited medication, exercise, diet, CPAP, and fiber inputs | Within-visit, about two-year visit prediction, six-month transfer, and 12-month monthly intervention trajectories | Correlation, top-k accuracy, C-index, MAE, treatment-direction agreement, and concordance with published RCT intervals | Predictive calibration NR; meaningful external cohort evaluation | Explicitly associational; incomplete dose, adherence, indication, and time-dependent confounding; repository placeholder but no usable public code |
| ChronoMedicalWorld [7] | arXiv v1; private KidneyOnline cohort with 2,232 patients and 15,070 patient-years | Annual kidney state; 62 medication indicators plus transcript embeddings | Next-year prediction and closed-loop annual rollout, maximum eight steps | MAE, RMSE, relative improvement, rollout MAE, and architecture/action ablations | Calibration NR; external validation NR | Explicitly non-causal; medication dose, duration, and adherence absent; code NR and data private |
| Intervention-Aware Clinical World Model [15] | MICCAI MWM Workshop / arXiv; DECAAF-II parent cohort 830, with 91 full-modality evaluation cases | Pre-ablation MRI latent, ablation map, covariates, event and ECG context; medication, cardioversion, and repeat-procedure events | Event updates to day 90; queries through day 210; recurrence to 451 days | AUROC, AUPRC, scar-extent MAE, Brier, ECE, edit sensitivity, fold and seed variation | Brier 0.201 and ECE 0.032; no external validation | Input edits described as associational; public code, patient data unavailable |
| MeWM [4] | ICCV 2025; 338 in-house paired TACE CT studies plus 78 public HCC-TACE-Seg cases | Pre-treatment CT and mask; TACE drug, dose, and embolic-material combinations | Single pre-to-post transition; beam-search action planning without calendar-time or multi-visit rollout | FID, LPIPS, radiologist classification, survival MSE/C-index/log-rank, protocol overlap metrics | Calibration NR; public cohort is adapted rather than zero-shot | Observational treatment pairs with no causal estimand or confounding adjustment; code public, governed data and weights incomplete |
| CLARITY [8] | arXiv v3, accepted to ECCV 2026; 203-patient MU-Glioma-Post, zero-shot 298-patient UCSF cohort, separate 985-patient ISPY-2 model | MRI latent, demographics, genomics, treatment history, time gap; constrained treatment proposals | Paired pre-to-post training and recursive policy rollout; inverse-survival search uses three iterations | Treatment overlap, C-index, Brier, log-rank, latent drift, image metrics, and 40-case expert preference | Brier reported; no ECE, reliability, interval coverage, or epistemic uncertainty; meaningful zero-shot external test | Uses “counterfactual” language without identification assumptions or confounding control; code public, raw data and required weights incomplete |

## Imaging and Embodied Studies

| Study | Status and data | State and action | Rollout | Main evidence | Calibration and external validation | Causal, control, and reproducibility boundary |
| --- | --- | --- | --- | --- | --- | --- |
| Brain-WM [9] | arXiv v1; 527 internal subjects and 61 external subjects across multiple institutions | Multisequence MRI, demographics, treatment history; next treatment and interval | One treatment-conditioned future-MRI transition; no recursive multi-treatment evaluation | Treatment metrics plus NMSE, PSNR, and SSIM against imaging baselines | Calibration NR; genuine multi-institution external evaluation | Retrospective conditioning without causal identification; code public, raw data access varies |
| Cardiac Copilot [10] | MICCAI 2024; 125 healthy-adult scans and about 188K image–pose pairs | One ultrasound frame; direct six-degree-of-freedom target-plane pose | One latent transition and direct-to-goal regression; no executed or closed-loop acquisition | Component-wise pose MAE and error dispersion | Calibration NR; held-out subjects in one restricted setting | No path, pressure, patient motion, or safety constraints; code and data release NR |
| EchoWorld [11] | CVPR 2025; 356 scans and about 1M image–pose pairs from healthy adult males | Current image or eight historical image–pose pairs; relative six-degree-of-freedom target pose | One sampled transition for pretraining; offline sequential prediction over recorded history | Translation and rotation MAE against single-frame and sequential baselines | Calibration NR; no external hospital or prospective execution | Imitation-style target pose, not executed control; code public, data restricted |
| SAW [12] | arXiv v1 under review; reports 12,044 clips from 101 videos | Initial frame, text, affordance mask, and prescribed 2-D tool-tip trajectory | One-shot 81-frame generation, about 3.24 seconds; no feedback | FVD variants, SSIM, PSNR, LPIPS, and downstream action-recognition F1 | Calibration NR; no independent external or clinician validation | Trajectory is not robot kinematics; dataset totals are internally inconsistent; code and curated release NR |
| Surg-UniWorld [13] | arXiv v1; Cholec80-SurgWAM with 6,001 49-frame clips | Initial frame, text, full future masks, and optional future edge, depth, or flow controls | One-shot 49-frame generation; no autoregressive or closed-loop control | PSNR, SSIM, LPIPS, FID, FVD, edge F1, depth error, and flow error | Calibration NR; held-out Cholec80 only | Future controls are derived visual constraints rather than actions; claimed code was NI and benchmark download NR |
| Surgical WAM [14] | arXiv v1; 10K SurRoL simulated demonstrations across four tasks | Endoscopic RGB, robot proprioception, goal; Cartesian pose, orientation, and gripper actions | Receding horizon predicts 16 steps, executes 4, and replans | Task success over 100 simulated episodes plus horizon and fine-tuning ablations | Calibration NR; closed-loop evaluation entirely simulated | Only study with executable closed-loop actions; no quantitative real-robot result; code, checkpoints, and processed data NR |

## Cross-Study Findings

### Action semantics

The word *action* covers different objects: recorded treatments, editable treatment tokens, procedure events, target poses, prescribed image trajectories, future masks, and executable robot commands. Only Surgical WAM evaluates executable actions in a closed loop. Surg-UniWorld's masks, depth, and flow are future visual constraints derived from target clips rather than interventions available to a controller.

### Causal validity

No study identifies a treatment-effect estimand. HealthFormer and ChronoMedicalWorld explicitly limit their interpretation to associations. Other treatment-conditioned systems likewise omit exchangeability, positivity, time-zero alignment, censoring, or overlap analysis. CLARITY's counterfactual terminology is therefore stronger than its identified evidence.

### Calibration and uncertainty

The postoperative cardiology model is the only study reporting ECE. CLARITY reports Brier score but no reliability curve, interval coverage, or epistemic uncertainty. No study measures calibrated uncertainty growth across autoregressive or recursive rollout.

### External validity

HealthFormer, CLARITY, and Brain-WM perform meaningful external-cohort evaluation. MeWM uses a public cohort after adaptation on most of that cohort. The remaining studies use internal, held-out, or simulated test sets.

### Horizon

Horizon is not standardized. It ranges from one future image or a three-second video clip to full hospitalization rollout, annual eight-step kidney trajectories, monthly physiology, and 90-day postoperative event updates. Sampling or diffusion solver steps should not be counted as clinical rollout steps.

### Reproducibility

Inspectable public code was found for five studies. Governed clinical data remain unavailable for most clinical systems, and several public repositories omit weights, derived data, or required metadata. SAW reports inconsistent clip totals, and Surgical WAM omits the scale of its first-stage video pretraining and quantitative real-video transfer.

## Source Anchors

- EHRWorld: Sections 3–5, limitations, and Appendices A–C.
- HealthFormer: Results and Methods, including intervention framework and availability statement.
- ChronoMedicalWorld: Sections 3–6.4.
- Intervention-Aware Clinical World Model: Sections 3–4.3.
- MeWM: Sections 3–4 and official ICCV record.
- CLARITY: Sections 3–4 and supplementary Sections 6–11.
- Brain-WM: Sections III–IV.
- Cardiac Copilot: Sections 2–3.
- EchoWorld: Sections 3–5 and supplement.
- SAW: Sections 2–4.
- Surg-UniWorld: Sections III–V.
- Surgical WAM: Sections 3–4.

