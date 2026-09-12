# Full-Text Eligibility Rubric

Snapshot date: 2026-09-12  
Input: `full-text-candidates.csv`  
Purpose: independent AI-assisted full-text eligibility assessment before author verification

## Core empirical inclusion

Include only when the primary text establishes all four:

1. **Medical scope:** the modeled system, data, task, or environment is medical, clinical, physiological, procedural, biomedical, or a health intervention.
2. **Learned dynamics:** the study learns or adapts a state transition, temporal rollout, future-observation generator, action-conditioned simulator, or model used for internal planning.
3. **Capability evaluation:** the study empirically evaluates future-state or future-observation prediction, free-running rollout, action response, alternative-action comparison, simulator fidelity, or model-based planning/control. Merely using a generative model as augmentation is insufficient unless its dynamics capability is evaluated.
4. **Stable primary text:** enough scholarly primary text and metadata are available to extract methods and results.

Static representation learning, iterative refinement of one observation, ordinary one-step prediction without a dynamics interpretation, and generic video generation described only as a precursor to a world model are excluded.

## Core review inclusion

Include a review only if medical or healthcare world models are its primary topic and it presents a field definition, taxonomy, evidence map, benchmark synthesis, or clinical-translation analysis.

## Publication lineage

Treat a preprint and its peer-reviewed version as one study. Retain the most complete stable version and identify duplicate or superseded records. Distinct benchmark, dataset, and model papers remain separate only when they make separately extractable empirical contributions.

## Evidence sources

Use the linked primary text first: official arXiv abstract/PDF/HTML, CVF Open Access, Springer proceedings, PubMed Central, publisher page, or official project repository when needed for artifact verification. Do not use secondary summaries to establish eligibility.

## Output schema

Write exactly one row per candidate:

```text
candidate_id,title,decision,corpus_type,primary_reason_code,evidence_for_dynamics,evidence_for_evaluation,publication_lineage,full_text_url,rationale
```

Allowed values:

- `decision`: `include`, `exclude`, or `uncertain`
- `corpus_type`: `empirical`, `review`, `not_applicable`, or `uncertain`

Allowed `primary_reason_code`:

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
- `policy_excluded`
- `uncertain`

Use concise paraphrases, not copied passages. Mark `uncertain` if the primary text is unavailable or internally inconsistent. This is AI-assisted screening and must not be described as human dual screening.
