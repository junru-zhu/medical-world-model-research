# Independent Inclusion-QC Rubric

Status date: 2026-09-12  
Purpose: conservative post-adjudication verification of every proposed inclusion

## Core rule

Retain a proposed empirical inclusion only when primary full text directly
supports all four conditions:

1. a substantive medical or biomedical modeled state;
2. a transition mechanism learned, fitted, calibrated, or adapted from
   observed data;
3. direct evaluation of evolving future state, recursive rollout,
   action/intervention response, simulator fidelity, or planning/control that
   depends on that learned transition; and
4. enough stable primary evidence to extract data, methods, and results.

The record must also meet the review's conceptual-equivalence boundary through
at least one route:

- explicit author framing as a world model, medical or biological
  digital/virtual twin, patient simulator, clinical trial simulator, or
  another reusable dynamic simulator of the modeled state; or
- use of the learned transition as the internal environment for iterative
  model-based planning or closed-loop control.

Ordinary disease-progression analysis, PK/PD, population simulation,
time-series forecasting, neural-dynamics estimation, and epidemiological
modeling are adjacent methods unless they meet one of those routes.

The following are not sufficient by themselves:

- the phrase “digital twin,” “patient simulator,” or “world model”;
- static prediction, classification, representation transfer, or one isolated
  endpoint;
- a fixed parametric trend or hand-specified mechanistic simulator with only a
  fitted scalar;
- policy learning that does not learn or adapt environment dynamics;
- generative augmentation without transition evaluation;
- a conference abstract, registry entry, commentary, or inaccessible source;
- a duplicate preprint or less complete publication version.

One-step prediction qualifies only when it is explicitly the next system state
under learned temporal or perturbation dynamics and that transition is directly
evaluated. Ordinary forecasting qualifies only when the model and evaluation
represent an evolving state rather than a collection of unrelated horizon
endpoints.

Retain a review only when learned or adapted medical/biomedical dynamics,
medical world models, action-conditioned patient simulators, or closely
equivalent systems are a central evidence category. Exclude generic reviews of
digital twins, forecasting, reinforcement learning, mechanistic models, or
virtual cells when learned transition and rollout evidence is peripheral.

## Required checks

For each proposed inclusion:

1. inspect the most complete stable primary text;
2. identify the learned/adapted transition and its data source;
3. identify the direct operational dynamics evaluation;
4. distinguish observed action, intended treatment, simulated control, and
   generated trajectory;
5. verify publication lineage and retain only the most complete version;
6. reject sources too thin for the 45-field extraction; and
7. write a concise full-text anchor that makes the boundary decision auditable.

## Output schema

Write one row per proposed inclusion, preserving input order:

```text
audit_id,title,qc_decision,qc_corpus_type,qc_reason_code,qc_rationale,full_text_anchor,confidence
```

Allowed values:

- `qc_decision`: `include`, `exclude`
- `qc_corpus_type`: `empirical`, `review`, `not_applicable`
- `confidence`: `high`, `medium`, `low`

Use a short descriptive `qc_reason_code`, such as:

- `learned_multistep_dynamics`
- `learned_one_step_state_transition`
- `action_conditioned_closed_loop_control`
- `substantive_dynamic_simulator_review`
- `static_or_endpoint_prediction`
- `no_learned_transition`
- `hand_specified_mechanistic_dynamics`
- `no_operational_dynamics_evaluation`
- `review_scope_too_broad`
- `duplicate_publication`
- `insufficient_primary_evidence`
- `wrong_domain`
- `outside_world_model_conceptual_boundary`

This remains AI-assisted quality control and does not replace qualified human
verification.
