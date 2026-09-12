# Idea-Grounding Packet

## Scope and Evidence Boundary

- Topic: evaluation and benchmarking of medical world models.
- Search date: 2026-09-12.
- Source-supported fact: broad medical-world-model reviews already exist.
- Source-supported fact: empirical systems span EHR, physiology, treatment-conditioned imaging, ultrasound guidance, surgical video, and simulated surgical control.
- Searcher inference: evaluation practice is sufficiently fragmented to support a focused review and benchmark paper.
- Unknown: whether a dedicated cross-domain medical-world-model evaluation benchmark is currently under review or unpublished.

## Evidence Cards

| Source | Supported observation | Reported limitation or boundary | Mechanism primitive | Protocol anchor | Confidence |
| --- | --- | --- | --- | --- | --- |
| Chen et al., 2026 review | The field contains distinct capability levels and heterogeneous validation settings | Broad review, not a dedicated metric audit | Capability hierarchy | 14 strict empirical studies | Direct |
| MeWM, ICCV 2025 | Treatment-conditioned tumor simulation can be linked to retrospective decision support | Image realism and historical agreement do not establish causal benefit | Policy plus generative dynamics | TACE oncology imaging | Direct |
| EHRWorld, 2026 | Long-horizon EHR simulation exhibits measurable error accumulation | Shared external benchmark and causal validation remain absent | Sequential conditional state update | MIMIC-derived EHR trajectories | Direct |
| HealthFormer, 2026 | A generative multimodal physiology model can answer forecasting and intervention-conditioned queries | Cohort access and transportability determine reproducibility | Autoregressive multimodal physiology | Multi-cohort transfer and intervention comparisons | Direct |
| ChronoMedicalWorld, 2026 | Structured and conversational actions can condition chronic-disease rollout | One disease and no alternative-action causal test | Latent transition with action encoder | CKD/eGFR long-horizon rollout | Direct |
| Brain-WM and CLARITY | Treatment-conditioned latent or image trajectories can support retrospective planning experiments | Treatment prediction may imitate practice; future-image quality is not treatment-effect validity | Joint dynamics and planning | Glioma longitudinal imaging | Direct |
| EchoWorld and Cardiac Copilot | World models can learn visual consequences of probe motion and improve navigation | Navigation performance is not a patient-outcome measure | Embodied visual-motion transition | Real echocardiography scans | Direct |
| SAW, Surg-UniWorld, and Surgical WAM | Surgical world models range from controllable video generation to simulated closed-loop control | Visual fidelity, physical safety, and clinical utility are different evidence levels | Action-conditioned video dynamics and receding-horizon control | Cholec80-derived or simulated tasks | Direct |

## Cross-Source Relations

| Source pair or cluster | Relation | Open gap or conflict | Why it matters | Evidence needed next |
| --- | --- | --- | --- | --- |
| Broad reviews vs. empirical papers | leaves-open | Reviews classify capabilities but do not normalize evaluation protocols | Supports a differentiated review | Full metric extraction |
| EHR models vs. oncology imaging models | conflicts-with | “Trajectory fidelity” is measured with incompatible event, scalar, image, and decision metrics | Cross-domain claims cannot be compared directly | Metric taxonomy and task cards |
| Action-conditioned models vs. causal treatment-effect methods | depends-on | Conditioning on recorded treatment is not sufficient for causal interpretation | Prevents overclaiming intervention benefit | Explicit estimand and confounding audit |
| Surgical video generation vs. Surgical WAM | supports | Better world modeling may help control, but generation metrics alone do not prove it | Motivates layered utility evaluation | Correlation between fidelity and control success |
| Development cohorts vs. external datasets | leaves-open | Most systems lack geographic and temporal external validation | Clinical translation requires transportability evidence | Multicenter benchmark |

## Idea Constraints

- Already-covered central claim: medical world models move medical AI from static prediction toward dynamic simulation.
- Already-covered taxonomy: patient state, dynamics, intervention conditioning, and planning.
- Transferable primitive: capability-specific evaluation rather than one aggregate score.
- Protocol anchors: MIMIC-IV/eICU for longitudinal EHR; OhioT1DM for explicit insulin and meal actions; EchoNet and Cholec80 for embodied or visual dynamics.
- Stale route: another architecture-centered narrative survey.
- Minimum viable review question:

  **What evidence is required to justify forecasting, action-conditioned, counterfactual, and planning claims made by medical world models?**

- Minimum viable original research question:

  **Do current model rankings remain stable when evaluation moves from one-step teacher-forced prediction to calibrated free-running rollouts under clinically meaningful action perturbations and external validation?**
