# Medical World-Model Research Team Workflow

## Objective

Produce two linked, publication-quality papers:

1. a scoping review that defines medical world-model capabilities, maps the
   reported evidence, and identifies a reproducible research gap; and
2. an original real-data study that addresses one selected gap without making
   claims beyond the design.

## Roles

### A — Research concept lead

Responsibilities:

- develop candidate medical world-model research questions;
- define the intended capability: passive forecasting, action-conditioned
  simulation, counterfactual comparison, or planning;
- state the scientific importance and the strongest claim the proposed design
  could support;
- maintain a short decision log for ideas accepted, revised, or rejected.

Deliverable: research concept brief with question, capability, expected
contribution, feasibility, and overclaim risks.

### B — Literature, evidence, and data lead

Responsibilities:

- run and document the literature search;
- verify publication lineage, metadata, and source status;
- summarize recent methods, datasets, evaluation practices, and competing
  reviews;
- identify accessible datasets and their licenses, provenance, cohort
  structure, missingness, action fields, and external-validation potential.

Deliverable: auditable evidence corpus, reference library, dataset cards, and
current-research-status report.

### C — Gap and study-design lead

Responsibilities:

- convert literature observations into explicit, measurable gaps;
- distinguish a missing report from a missing scientific capability;
- compare candidate gaps by recurrence, importance, data feasibility,
  measurable failure modes, and overclaim risk;
- define research questions, estimands, outcome hierarchy, analyses, and claim
  boundaries before final experiments.

Deliverable: gap-selection audit, protocol, frozen analysis specification, and
amendment log.

### D — Experiment and reproducibility team (one or two people)

Responsibilities:

- audit and prepare the real dataset without leakage;
- implement baselines and proposed model families;
- verify rollout semantics, support alignment, metrics, calibration, and
  physiological checks;
- run the frozen seed matrix and prespecified sensitivity analyses;
- retain checkpoints, patient-level derived metrics, logs, and exact commands.

Deliverable: reproducible experiment package, frozen result tables, figures,
and technical validation report.

The two experiment members should divide implementation and verification where
possible. The verifier independently checks indexing, split isolation,
aggregation, and result-file provenance rather than only reviewing code style.

### E — Scientific writing lead

Responsibilities:

- write from frozen evidence and generated tables rather than manually copied
  intermediate numbers;
- keep Results claim-driven and Discussion synthesis-driven;
- report negative and null findings;
- maintain consistent terminology, citations, figure legends, declarations,
  data availability, and reporting-checklist material;
- ensure every conclusion stays within the capability actually tested.

Deliverable: complete review manuscript, complete original manuscript, and
submission-ready supplementary text.

The writing lead may request clarification or additional prespecified output
but cannot silently redefine outcomes after seeing results.

### F — Independent scientific reviewers (two people)

Reviewer 1 focuses on:

- clinical and scientific importance;
- validity of the capability claim;
- dataset relevance, external validity, safety interpretation, and clinical
  overclaim.

Reviewer 2 focuses on:

- methods, statistics, reproducibility, leakage, aggregation, calibration,
  sensitivity analyses, and consistency between code, tables, figures, and
  prose.

Deliverable: independent review reports with prioritized major and minor
concerns, followed by a documented author response and re-review.

Reviewers should not be the primary implementers of the analyses they are
assigned to audit.

## Stage gates

### Gate 1 — Review question and protocol

Required:

- explicit eligibility criteria and search strategy;
- frozen capability definitions and evidence domains;
- documented screening, extraction, adjudication, and correction process.

### Gate 2 — Review manuscript

Required:

- complete corpus and reference linkage;
- evidence counts reproducible from source tables;
- independent methodological and domain review;
- venue-limit and reporting-checklist validation.

Human database updates, clinical review, and author declarations remain
separate submission gates.

### Gate 3 — Gap selection and experiment freeze

Required:

- selected gap traceable to the review;
- real dataset verified and legally usable;
- no leakage between development, calibration, and test partitions;
- fixed questions, metrics, models, seeds, comparisons, bootstrap procedure,
  and sensitivity analyses;
- amendment log identifying any post-pilot adaptation.

### Gate 4 — Result freeze

Required:

- all expected model-seed runs complete;
- stale or cross-wired artifacts rejected automatically;
- raw and recalibrated invariance checks pass;
- patient-level support and aggregation verified;
- prespecified Monte Carlo and implementation-seed sensitivities complete.

### Gate 5 — Original manuscript

Required:

- every number generated from frozen result artifacts;
- figures pass source, alignment, text-size, collision, and visual audits;
- negative results retained;
- independent results-and-claims review completed;
- no treatment-effect, counterfactual, policy, clinical-benefit, or deployment
  statement unless separately identified by an appropriate design.

### Gate 6 — Submission authorization

Required from the human research team:

- final authors, affiliations, corresponding author, and CRediT roles;
- funding, acknowledgements, and competing interests;
- ethics or institutional determination;
- healthcare-professional and domain-expert approval;
- stable repository and data-access statement;
- final target-journal rule check and explicit authorization to submit.

## Decision rule

No role may strengthen the scientific claim merely to make the story more
attractive. When evidence supports a narrower or negative conclusion, the
manuscript changes—not the frozen analysis.
