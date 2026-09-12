# Search Notes

Date: 2026-09-12

## Safe Queries Used

- medical world model patient trajectory clinical
- healthcare world model EHR longitudinal
- medical world model imaging intervention
- surgical world model action-conditioned video
- medical world model benchmark evaluation
- clinical world model calibration long-horizon rollout
- patient digital twin generative longitudinal model
- official dataset pages for MIMIC-IV, eICU, HiRID, OhioT1DM, EchoNet-Dynamic, MIMIC-CXR, and Cholec80
- direct title and identifier searches for the closest papers

## Sources Checked

- arXiv title, abstract, and HTML records
- CVF Open Access for ICCV and CVPR papers
- Springer chapter page for MICCAI
- PMLR and PubMed for adjacent longitudinal and generative-health work
- PhysioNet dataset records
- Stanford AIMI dataset records
- Official OhioT1DM dataset page

## Screening Boundary

- This was a targeted standard search for scope and novelty grounding, not a completed systematic review.
- The retained table emphasizes sources that change the review boundary, evaluation framework, dataset choice, or original-paper design.
- Three broad reviews were treated as direct novelty risks.
- Twelve representative empirical systems were retained across EHR, physiology, oncology imaging, echocardiography, and surgery.
- Static medical prediction, ordinary image generation, and general medical LLM papers were excluded unless they supplied a necessary baseline or evaluation principle.

## Exclusions

- Policy-excluded publishers and journals were not retained.
- Search snippets without a stable primary record were not used as evidence.
- Static classifiers and single-endpoint predictors without learned state transitions were excluded from the core medical-world-model set.
- Conventional digital-twin and treatment-effect papers were treated as adjacent methods unless they implemented a learned rollout or transition system.

## Unknowns and Required Follow-up

- Full metric extraction from every retained empirical paper is not yet complete.
- Code and data availability require paper-by-paper verification.
- Cholec80's current authoritative access page and terms need verification.
- The current version and publication status of several 2026 preprints may change.
- Search coverage after 2026-09-12 is outside this report.
- No target review venue has been selected; article length and review methodology must be aligned after venue selection.

## Handoff Notes

### For review writing

- Organize around evaluation claims, not model architectures.
- Open with the difference between plausible rollout and clinically valid simulation.
- Use the three existing broad reviews as the novelty boundary.
- Include a study-level evidence table and dataset fitness table.

### For experiment design

- Preferred benchmark route: MIMIC-IV development plus eICU external validation, subject to access.
- Lower-friction action-semantic route: OhioT1DM, with the limitation of 12 participants.
- Minimum metrics should include teacher-forced accuracy, free-running horizon degradation, calibration, clinical constraint violations, action sensitivity, and subgroup/external validation.
- Do not describe observational treatment substitutions as causal counterfactuals without an explicit estimand and assumptions.

### For review

- The main reviewer risk is novelty relative to the three broad 2025–2026 reviews.
- The defense must be concrete: this paper audits evaluation practice and produces a reusable metric and dataset framework.

