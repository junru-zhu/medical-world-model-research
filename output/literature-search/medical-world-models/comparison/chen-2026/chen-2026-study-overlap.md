# Study-level overlap with Chen et al. (2026)

## Reconstruction status

Chen et al. report a nested strict empirical subset of 14 studies but do not provide an explicit machine-readable roster. This is a high-confidence reconstruction from the official article PDF: ten studies are listed in the representative-model table and four additional studies are named in the empirical synthesis, matching the reported total of 14. It should not be described as an author-supplied inclusion list.

Source PDF: `output/literature-search/medical-world-models/sources/chen-2026-medical-world-models-in-healthcare.pdf`

## Provisional overlap

- Comparison-review studies reconstructed: 14
- Included in our current empirical corpus: 13 (92.9%)
- Located but excluded by our operational eligibility rule: 1
- Not located: 0
- Current empirical corpus size: 50
- Provisional title-level Jaccard overlap: 13/51 (25.5%)

These figures are provisional because our expanded search audit is still active. The Jaccard value is descriptive, not a comparative quality score: the reviews use different eligibility boundaries, search dates, and corpus roles.

## Study dispositions

| Reconstructed Chen et al. study | Source basis | Our disposition | Reason code |
|---|---|---|---|
| Cardiac Copilot: Automatic Probe Guidance for Echocardiography with World Model | representative-model table (p. 20) | included | — |
| EHRWorld: A Patient-Centric Medical World Model for Long-Horizon Clinical Trajectories | representative-model table (p. 20) | included | — |
| EchoJEPA: A Latent Predictive Foundation Model for Echocardiography | representative-model table (p. 20) | exclude | static_prediction |
| Brain-WM: Brain Glioblastoma World Model | representative-model table (p. 20) | included | — |
| CLARITY: Medical World Model for Guiding Treatment Decisions by Modeling Context-Aware Disease Trajectories in Latent Space | representative-model table (p. 20) | included | — |
| Xray2Xray: World Model from Chest X-rays with Volumetric Context | representative-model table (p. 20) | included | — |
| EchoWorld: Learning Motion-Aware World Models for Echocardiography Probe Guidance | representative-model table (p. 20) | included | — |
| Medical World Model | representative-model table (p. 20) | included | — |
| SAW: Toward a Surgical Action World Model via Controllable and Scalable Video Generation | representative-model table (p. 20) | included | — |
| ChronoMedicalWorld: A Medical World Model for Learning Patient Trajectories from Longitudinal Care Data | representative-model table (p. 20) | included | — |
| Treatment-Aware Diffusion Probabilistic Model for Longitudinal MRI Generation and Diffuse Glioma Growth Prediction | treatment-response empirical synthesis (p. 24-25) | included | — |
| Surgical Vision World Model | action-semantics empirical synthesis (p. 25) | included | — |
| Policy4OOD: A Knowledge-Guided World Model for Policy Intervention Simulation against the Opioid Overdose Crisis | planning empirical synthesis (p. 19) | included | — |
| World Model Enhanced Offline Reinforcement Learning for Sequential Intervention Optimization in Acute Kidney Injury | counterfactual/planning empirical synthesis (p. 18, 36) | included | — |

## Boundary difference

The only reconstructed strict-subset study not included in our current empirical corpus is EchoJEPA. It was located through citation chasing and independently screened, then excluded at adjudication because the reported evaluation assessed representation transfer and robustness rather than future-state rollout, action-response simulation, or planning. This difference is substantive rather than a search miss: Chen et al. admit an L1 predictive-representation capability, whereas our operational corpus requires direct empirical evaluation of modeled state evolution or interaction.

## Interpretation

The 13/14 overlap supports strong recovery of the field's established anchor studies. The much larger current corpus reflects our broader operational search across medical, physiological, and procedural systems, but its final size and interpretation must remain unfrozen until the expanded alternate-term screen, full-text review, and adjudication are complete.
