# Title/Abstract Screening Rubric

Snapshot date: 2026-09-12  
Input: `candidates.csv`  
Purpose: provisional AI-assisted screening before author verification and full-text review

## Eligible core empirical record

Retain a record when the title or abstract indicates all of the following, or when the record plausibly may satisfy them and full text is needed:

1. medical, clinical, physiological, procedural, or biomedical data or environment;
2. a learned or adapted state-transition, temporal rollout, or action-conditioned generative mechanism;
3. evaluation of a future state or observation, action response, counterfactual comparison, simulator, or planning/control capability; and
4. a primary empirical study with enough metadata to seek the full text.

The model need not use the exact phrase “medical world model” if the abstract clearly describes a qualifying learned dynamics model.

## Eligible core review record

Retain a review only when medical or healthcare world models are its primary topic and it contributes a field definition, taxonomy, evidence map, benchmark analysis, or clinical-translation synthesis.

## Exclude

Exclude records that are clearly:

- non-medical;
- static classifiers, regressors, segmenters, or risk scores without learned temporal evolution;
- ordinary one-step sequence prediction without rollout, transition, simulator, or world-model interpretation;
- image or text generation without temporal or action-conditioned dynamics;
- conceptual or commentary records without empirical evaluation, unless eligible for the core review corpus;
- broad world-model or medical-AI reviews in which medical world models are not the primary topic;
- datasets, protocols, editorials, theses, patents, or duplicate publication-lineage records that do not add an eligible primary study;
- policy-excluded sources.

At title/abstract stage, favor sensitivity: use `uncertain` when the abstract is absent or the dynamics/evaluation criteria cannot be decided without full text.

## Required output

Write one row per input candidate, preserving `candidate_id` and `title`, with columns:

```text
candidate_id,title,decision,corpus_type,reason_code,rationale,full_text_needed
```

Allowed values:

- `decision`: `include`, `exclude`, or `uncertain`
- `corpus_type`: `empirical`, `review`, `not_applicable`, or `uncertain`
- `full_text_needed`: `yes` or `no`

Use one primary `reason_code`:

- `include_empirical`
- `include_review`
- `wrong_domain`
- `no_world_model_dynamics`
- `static_prediction`
- `no_empirical_evaluation`
- `review_not_primary`
- `duplicate_publication`
- `inaccessible_metadata`
- `policy_excluded`
- `uncertain`

Keep the rationale specific and no longer than one sentence. Do not inspect or copy another reviewer's decisions.
