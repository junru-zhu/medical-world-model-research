# Expanded-Search Full-Text Eligibility Rubric

Snapshot date: 2026-09-12  
Input: `comparison/full-text-candidates.csv`  
Purpose: two independent AI-assisted full-text assessments before third-review adjudication and author verification

## Empirical inclusion

Include an empirical study only when the primary text establishes all four:

1. **Medical or biomedical scope:** the modeled state belongs to a patient, physiological or cellular system, clinical process, medical procedure, healthcare system, or health intervention.
2. **Learned or adapted dynamics:** transition behavior is learned, fitted, calibrated, or otherwise adapted from observed medical or biomedical data. A wholly hand-specified mechanistic simulator is insufficient.
3. **Operational dynamics evaluation:** the study directly evaluates future-state or future-observation trajectories, recursive or free-running rollout, action/intervention response, alternative-action comparison, simulator fidelity, or planning/control that depends on the learned dynamics.
4. **Stable primary evidence:** sufficient scholarly primary text is available to verify methods, data, and results.

Do not include:

- static classification, segmentation, detection, representation transfer, or isolated endpoint prediction;
- generative augmentation without direct evaluation of temporal or action-conditioned dynamics;
- ordinary forecasting that does not model and evaluate evolving state;
- hand-specified Markov, compartmental, agent-based, or physiological simulators with no data-fitted transition component;
- commercial, behavioral, ecological, or engineering dynamics lacking a substantive medical or biomedical modeled state;
- protocols, editorials, issue records, abstracts without extractable methods/results, or duplicate publication versions.

One-step prediction can qualify only when the predicted object is explicitly the next system state under learned temporal or perturbation dynamics and that transition capability is directly evaluated. A model need not use the phrase “world model.”

## Review inclusion

Include a review only if it substantially synthesizes learned or adapted medical/biomedical dynamic simulators, medical world models, action-conditioned patient simulators, or closely equivalent systems. A general digital-twin, virtual-cell, reinforcement-learning, forecasting, or mechanistic-model review is insufficient unless learned transition/rollout systems are a central evidence category.

## Publication lineage

Merge preprints and peer-reviewed versions of the same study. Retain the most complete stable version. Treat a dataset or benchmark paper as a separate study only if it reports a separately extractable empirical contribution that satisfies the operational criteria.

## Evidence hierarchy

Use the primary full text first: publisher article, PubMed Central, official proceedings, arXiv HTML/PDF, or an official repository needed to verify an artifact. Secondary summaries may help locate a source but cannot establish eligibility.

## Required output

Write exactly one row per candidate, preserving candidate order, with this schema:

```text
audit_id,route,title,decision,corpus_type,reason_code,dynamics,evaluation,lineage,full_text_url,rationale,confidence
```

Allowed values:

- `decision`: `include`, `exclude`, `uncertain`
- `corpus_type`: `empirical`, `review`, `not_applicable`, `uncertain`
- `confidence`: `high`, `medium`, `low`

Allowed `reason_code`:

- `include_empirical`
- `include_review`
- `wrong_domain`
- `no_learned_dynamics`
- `no_future_or_action_evaluation`
- `no_primary_empirical_evaluation`
- `review_not_primary`
- `duplicate_publication`
- `inaccessible_full_text`
- `unstable_record`
- `uncertain`

Use concise paraphrases rather than copied passages. Choose `uncertain` when the primary text is inaccessible or does not permit a defensible decision. This is AI-assisted screening and must not be described as human dual screening.
