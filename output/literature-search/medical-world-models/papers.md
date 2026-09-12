# Literature Search: Evaluation and Benchmarking of Medical World Models

Date: 2026-09-12  
Search purpose: Establish a publishable review scope, identify recent empirical medical world models, map datasets and evaluation protocols, and derive an original-paper opportunity.  
Target venue/family: Biomedical AI, medical informatics, or digital-health review venue; exact venue remains to be selected.  
Source-quality policy: Primary proceedings, arXiv records, PubMed-indexed articles, official dataset pages, and established publishers were prioritized. Policy-excluded sources were not retained.

## Summary

- A generic review titled simply around “medical world models” is no longer sufficiently differentiated. At least three broad reviews or roadmaps appeared between late 2025 and August 2026.
- The empirical field is growing quickly across longitudinal EHRs, multimodal physiology, oncology imaging, echocardiography, and surgical interaction.
- Evaluation remains fragmented. Each paper uses domain-specific fidelity or downstream metrics, while trajectory calibration, action validity, rollout stability, counterfactual validity, external validation, and decision utility are rarely assessed together.
- The strongest review opportunity is therefore:

  **Evaluating Medical World Models: Datasets, Metrics, Causal Validity, and Safety for Long-Horizon Clinical Simulation**

- The strongest original-paper route is a reusable evaluation protocol or benchmark rather than another unconstrained model:

  **MedWM-Eval: Benchmarking Action-Conditioned Clinical Rollouts on Real Longitudinal Data**

## Paper Table

| # | Title | Year | Venue/source | Link | Type | Overall | Relevance note |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Beyond Generative AI: World Models for Clinical Prediction, Counterfactuals, and Planning | 2025 | arXiv preprint | https://arxiv.org/abs/2511.16333 | survey | Risk | Introduces an L1–L4 capability rubric and already covers imaging, EHRs, and surgery. A new broad review must offer a materially different synthesis. |
| 2 | Medical World Models: Representing Medical States, Modelling Clinical Dynamics and Guiding Intervention Policies | 2026 | arXiv preprint | https://arxiv.org/abs/2606.16721 | survey | Risk | Organizes the field around state construction, dynamics, and intervention policies. It is close to a general roadmap paper. |
| 3 | Medical World Models in Healthcare: Foundations, Applications, and Challenges for Trustworthy Clinical Translation | 2026 | arXiv preprint | https://arxiv.org/abs/2607.25242 | survey | Risk | Reports a structured narrative synthesis of 98 sources and 14 strict empirical studies. It is the closest competing review and makes a generic survey redundant. |
| 4 | Medical World Model | 2025 | ICCV 2025 | https://openaccess.thecvf.com/content/ICCV2025/html/Yang_Medical_World_Model_ICCV_2025_paper.html | method + benchmark | A | MeWM combines a treatment policy model with a tumor dynamics model for TACE planning. Evaluation mixes image realism, survival-related inverse dynamics, and clinician decision support. |
| 5 | EHRWorld: A Patient-Centric Medical World Model for Long-Horizon Clinical Trajectories | 2026 | arXiv preprint | https://arxiv.org/abs/2602.03569 | method + benchmark | A | Models long-horizon EHR trajectories and explicitly studies error accumulation, clinical-event stability, and intervention-conditioned state updates. |
| 6 | Simulating Clinical Interventions with a Generative Multimodal Model of Human Physiology | 2026 | arXiv preprint | https://arxiv.org/abs/2604.27899 | method + benchmark | A | HealthFormer models 667 measurements over multimodal longitudinal physiology and evaluates transfer plus intervention-conditioned predictions. |
| 7 | ChronoMedicalWorld: A Medical World Model for Learning Patient Trajectories from Longitudinal Care Data | 2026 | arXiv preprint | https://arxiv.org/abs/2605.21963 | method + benchmark | A | Uses action-conditioned latent transitions for chronic-disease trajectories and tests long-horizon CKD rollout, but not alternative-treatment causal validity. |
| 8 | CLARITY: Medical World Model for Guiding Treatment Decisions by Modeling Context-Aware Disease Trajectories in Latent Space | 2026 version | arXiv preprint | https://arxiv.org/abs/2512.08029 | method + benchmark | A | Connects treatment-conditioned latent rollouts to candidate treatment planning in glioma. Strongly relevant to evaluation of counterfactual claims. |
| 9 | Brain-WM: Brain Glioblastoma World Model | 2026 | arXiv preprint | https://arxiv.org/abs/2603.07562 | method + benchmark | A | Jointly predicts treatment and future MRI across internal and external cohorts. Its treatment-prediction target may partly measure historical clinician behavior rather than optimal action. |
| 10 | Cardiac Copilot: Automatic Probe Guidance for Echocardiography with World Model | 2024 | MICCAI 2024 | https://link.springer.com/chapter/10.1007/978-3-031-72378-0_18 | pure method | A | A peer-reviewed embodied medical world model using real probe-motion data. Evaluation focuses on navigation error rather than patient outcomes. |
| 11 | EchoWorld: Learning Motion-Aware World Models for Echocardiography Probe Guidance | 2025 | CVPR 2025 | https://openaccess.thecvf.com/content/CVPR2025/html/Yue_EchoWorld_Learning_Motion-Aware_World_Models_for_Echocardiography_Probe_Guidance_CVPR_2025_paper.html | method + benchmark | A | Predicts motion-induced visual changes and evaluates sequential probe guidance on more than one million ultrasound images. |
| 12 | SAW: Toward a Surgical Action World Model via Controllable and Scalable Video Generation | 2026 | arXiv preprint | https://arxiv.org/abs/2603.13024 | method + benchmark | A | Conditions surgical video generation on actions, affordances, and trajectories; evaluates generation fidelity and downstream rare-action recognition. |
| 13 | Surg-UniWorld: A Unified Surgical World Model with Multimodal Control Experts | 2026 | arXiv preprint | https://arxiv.org/abs/2608.06770 | method + benchmark | A | Introduces Cholec80-SurgWAM and evaluates multimodal controllability, temporal consistency, and visual quality. |
| 14 | Surgical WAM: A World-Action Model for Data-Efficient Surgical Robot Learning | 2026 | arXiv preprint | https://arxiv.org/abs/2608.11204 | method + benchmark | A | Extends surgical world modeling to receding-horizon closed-loop control in four simulated tasks, exposing a distinction between video realism and control utility. |
| 15 | Intervention-Aware Clinical World Model for Post-Op Outcome Forecasting in Cardiology | 2026 | MICCAI 2026 MWM Workshop / arXiv | https://arxiv.org/abs/2608.13518 | method + benchmark | A | Uses a structured latent state updated by irregular postoperative events. Evaluation is internal cross-validation on DECAAF-II; external and prospective validity remain open. |

## Closest-Work Clusters

### Cluster 1: Broad definitions and capability taxonomies

- Representative papers: Qazi et al.; Liu et al.; Chen et al.
- What is already covered: definitions, state–dynamics–action architectures, application domains, capability levels, and high-level clinical-translation challenges.
- Remaining gap: no dedicated cross-study synthesis of evaluation design, dataset fitness, metric validity, and minimum evidence for claims at different capability levels.
- Differentiation route: make evaluation—not architecture—the organizing principle.
- Effect on our review: do not claim to be the first general review of medical world models.

### Cluster 2: Longitudinal EHR and physiology simulators

- Representative papers: EHRWorld, HealthFormer, ChronoMedicalWorld, and the intervention-aware cardiology model.
- What is already covered: multi-step patient-state forecasting, event-conditioned updates, multimodal physiological modeling, and intervention-conditioned queries.
- Remaining gap: inconsistent definitions of an action, incompatible prediction horizons, limited calibration reporting, weak cross-site validation, and no shared rollout benchmark.
- Differentiation route: audit state fidelity, action semantics, horizon-dependent degradation, uncertainty, and external validation separately.

### Cluster 3: Treatment-conditioned oncology imaging

- Representative papers: MeWM, CLARITY, and Brain-WM.
- What is already covered: treatment-conditioned image or latent-state prediction and retrospective treatment-planning experiments.
- Remaining gap: visual realism and agreement with recorded treatments do not establish causal treatment benefit. Existing studies use different image, survival, treatment, and clinician metrics.
- Differentiation route: separate observation realism, biological trajectory validity, counterfactual validity, and clinical decision utility.

### Cluster 4: Embodied ultrasound and surgical world models

- Representative papers: Cardiac Copilot, EchoWorld, SAW, Surg-UniWorld, and Surgical WAM.
- What is already covered: action-conditioned visual prediction, probe guidance, surgical video generation, and simulated closed-loop control.
- Remaining gap: no shared evaluation bridge from perceptual fidelity to task success, physical safety, robustness, and clinical workflow outcomes.
- Differentiation route: propose a layered evaluation ladder for perception, dynamics, control, safety, and human-supervised clinical utility.

## Opportunity Map

| Cluster | Status | Open gap | Possible direction | Evidence needed | Risk |
| --- | --- | --- | --- | --- | --- |
| General medical-world-model surveys | covered central claim | Broad field definitions and roadmaps already exist | Do not write another generic survey | Compare review scopes and search cutoffs | High novelty risk |
| Evaluation methodology | benchmark gap | No common framework joins trajectory fidelity, action validity, calibration, causal claims, and decision utility | Evaluation-focused scoping review plus reporting checklist | Full metric extraction from empirical studies | Low-to-moderate risk |
| Long-horizon clinical rollout | crowded but open | Error propagation and calibration are measured inconsistently | Horizon-stratified benchmark with teacher-forced and free-running rollouts | Real longitudinal dataset and strong baselines | Moderate execution risk |
| Intervention-conditioned simulation | mechanism gap | Models condition on treatments but often lack explicit causal estimands | Distinguish associational actions from counterfactual interventions | Target-trial or randomized evidence where available | High causal risk |
| Medical world-model datasets | benchmark gap | Datasets differ in modality, time scale, action observability, and accessibility | Dataset fitness matrix and benchmark task cards | Verified data dictionaries and access terms | Moderate |
| Embodied medical systems | deployment/system gap | Simulation metrics do not reliably predict physical or clinical safety | Layered evaluation from visual dynamics to closed-loop safety | Real-device or high-fidelity simulator validation | High resource risk |

## Benchmark and Dataset Candidates

| Name | Link | Task opportunity | Candidate metrics | Fit | Access and risks |
| --- | --- | --- | --- | --- | --- |
| MIMIC-IV v3.1 | https://physionet.org/content/mimiciv/ | ICU/ED state-transition and intervention-conditioned event rollout | Per-variable error, event F1, calibration, horizon degradation, constraint violations | High | Credentialed access; observational actions are confounded; no ground-truth alternative outcomes |
| eICU-CRD v2.0 | https://physionet.org/content/eicu-crd/ | Multicenter external validation of ICU dynamics | Cross-site degradation, subgroup calibration, trajectory fidelity | High as external validation | Credentialed; site interfaces create informative missingness |
| HiRID v1.1.1 | https://physionet.org/content/hirid/ | High-frequency physiological and treatment dynamics | Multi-horizon forecasting, intervention response, uncertainty | High | Contributor-reviewed access; single center; dense but irregular clinical processes |
| OhioT1DM | https://webpages.charlotte.edu/rbunescu/data/ohiot1dm/OhioT1DM-dataset.html | Glucose world model conditioned on insulin, meals, exercise, sleep, and stress | Glucose MAE/RMSE, hypoglycemia recall, calibration, action sensitivity, rollout stability | High for explicit actions | Real data but only 12 people and eight weeks each; DUA required |
| MIMIC-CXR-JPG v2.1.0 | https://physionet.org/content/mimic-cxr-jpg/ | Longitudinal chest-image state prediction linked to EHR events | Image/label trajectory consistency, temporal ordering, clinical event alignment | Medium | Credentialed; many patients lack dense serial imaging; treatment causality is weak |
| EchoNet-Dynamic | https://aimi.stanford.edu/datasets/echonet-dynamic-cardiac-ultrasound | Cardiac video dynamics and state representation | EF/volume error, temporal consistency, robustness | Medium | More than 10,000 videos, but no probe-motion action stream in the standard dataset |
| Cholec80 | Dataset access must be verified with the current owner | Surgical visual dynamics and action recognition | FVD-style fidelity, temporal consistency, action controllability, downstream recognition | Medium-to-high | Video annotations exist, but robot kinematics and physical interaction labels are limited; access terms require verification |

## Review Contribution Proposed

The review should contribute four concrete artifacts:

1. **A claim-to-evidence hierarchy** distinguishing forecasting, action conditioning, counterfactual comparison, and closed-loop planning.
2. **An evaluation cube** covering state, transition, action, rollout, uncertainty, causal validity, external validity, and decision utility.
3. **A dataset fitness matrix** showing which datasets can and cannot support each type of claim.
4. **A minimum reporting checklist**, provisionally named **MedWM-Eval**, for reproducible evaluation of medical world models.

## Citation and Positioning Cautions

- “World model” should require an explicit learned state-transition or rollout mechanism; static prediction and ordinary representation learning are adjacent work, not automatically medical world models.
- Action-conditioned prediction is not equivalent to causal counterfactual inference.
- Agreement with historical treatments can measure clinician imitation rather than treatment optimality.
- Image realism does not establish biological or therapeutic validity.
- Internal retrospective validation does not establish clinical benefit.
- No current dataset provides observed outcomes for every alternative intervention on the same patient; counterfactual claims require explicit assumptions or experimental evidence.

