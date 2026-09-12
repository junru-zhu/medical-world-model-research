# Exhaustive Primary-Filter Rescreen Rubric

Snapshot date: 2026-09-12  
Input: `candidates.csv`  
Purpose: correct the invalid automated discovery filter by independently screening every remaining excluded record

## Why this rescreen is required

The stratified filter audit identified eligible empirical studies and reviews in random samples from both automated-exclusion strata. The phrase and medical-term filter therefore cannot be retained as a definitive eligibility decision. Records already covered by the completed filter audit or the active expanded alternate-term screen are removed from this file; all other original exclusions are included.

## Conservative title/abstract decision

Choose `include` or `uncertain` whenever the title or abstract plausibly describes:

- a learned, fitted, calibrated, or data-adapted model of evolving medical, physiological, cellular, procedural, healthcare, or intervention states;
- future-state or trajectory generation, disease progression simulation, patient simulation, action/intervention response, model-based planning, or learned control;
- a review centrally synthesizing medical/biomedical world models, learned patient simulators, learned digital twins, learned dynamic disease models, or equivalent transition/rollout systems.

Choose `exclude` only when the record is clearly:

- non-medical or non-biomedical;
- static classification, detection, segmentation, representation, or isolated endpoint prediction;
- a hand-specified mechanistic, Markov, compartmental, economic, or agent-based model with no indication of learned, fitted, calibrated, or data-adapted transitions;
- a protocol, editorial, issue record, correction, or other item without a primary empirical or review contribution;
- unrelated to dynamic state evolution, rollout, action response, intervention simulation, or planning.

Do not require the phrase “world model.” Do not decide final eligibility from title/abstract ambiguity; use `uncertain` and retain for full-text review.

## Required output

Write exactly one row per candidate, preserving candidate order:

```text
audit_id,route,title,decision,corpus_type,reason_code,rationale
```

Allowed values:

- `decision`: `include`, `exclude`, `uncertain`
- `corpus_type`: `empirical`, `review`, `not_applicable`, `uncertain`

Allowed `reason_code`:

- `potential_empirical`
- `potential_review`
- `wrong_domain`
- `static_or_isolated_prediction`
- `no_learned_or_adapted_dynamics`
- `no_primary_contribution`
- `review_not_primary`
- `duplicate_or_issue_record`
- `insufficient_abstract`

Use concise paraphrases. This is AI-assisted screening and must not be described as human dual screening.
