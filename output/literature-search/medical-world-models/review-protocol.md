# Scoping Review Protocol: Evaluation of Medical World Models

Status: Corrected corpus, extraction, coding, analyses, references, figures, and manuscript regenerated; human verification pending; not registered  
Protocol date: 2026-09-12  
Reporting framework: PRISMA-ScR  
Canonical manuscript: `manuscript/review.md`

## Objective

Map how empirical medical world models define their state, actions, rollout regime, and capability claims, then determine what evidence is reported for dynamics, uncertainty, causal interpretation, external validity, decision utility, and safety.

## Primary Review Question

What evidence is reported, and what evidence remains missing, when medical world models make passive forecasting, action-conditioned simulation, counterfactual comparison, or closed-loop planning claims?

## Secondary Questions

1. How do studies operationally define a medical world model?
2. Which datasets, modalities, actions, horizons, baselines, and metrics are used?
3. How often are free-running rollout, calibration, external validation, causal assumptions, decision utility, and safety evaluated?
4. Which evidence requirements are shared across domains, and which require EHR-, imaging-, ultrasound-, or surgical-control-specific protocols?
5. How does an evaluation-centered synthesis differ from existing architecture- and application-centered reviews?

## Corpus Structure

### Core empirical corpus

A study enters the core corpus when it satisfies all criteria:

1. It uses medical, clinical, physiological, procedural, or biomedical data.
2. It learns or adapts a state-transition, temporal rollout, or action-conditioned generative mechanism.
3. It evaluates at least one future-state, future-observation, action-response, counterfactual, or planning capability.
4. Sufficient primary text is available to extract methods and evaluation details.

#### World-model equivalence clarification

The expanded alternate-term search retrieved a much broader literature on
ordinary forecasting, PK/PD, disease progression, epidemiology, mechanistic
simulation, and latent-process modeling. Before any corrected corpus count was
frozen, the phrase “closely equivalent system” was therefore made operational.
In addition to the four criteria above, an empirical study must satisfy at
least one conceptual-identity condition:

1. the authors explicitly frame the learned dynamic system as a world model,
   medical or biological digital/virtual twin, patient simulator, clinical
   trial simulator, or another reusable dynamic simulator of the modeled
   state; or
2. the learned transition is used as the internal environment for iterative
   model-based planning or closed-loop control.

Conventional disease-progression analysis, PK/PD, population simulation,
time-series forecasting, neural-dynamics estimation, or epidemiological
modeling remains bridge methodology unless it meets one of those conditions.
This clarification preserves the original separation between core medical
world models and adjacent dynamic modeling; it is not based on model
performance or study outcome.

### Core review corpus

Reviews enter the comparison corpus when medical world models are their primary topic and they provide a field definition, taxonomy, evidence map, or clinical-translation synthesis.

### Bridge methodology corpus

Adjacent work is retained when it supports evaluation design but does not qualify as a core medical world model. Bridge topics include:

- longitudinal prediction and disease-progression modeling;
- medical digital twins;
- dynamic treatment regimes and causal inference;
- target-trial emulation;
- uncertainty and calibration;
- decision-curve analysis and clinical utility;
- model-based control and simulator validation;
- clinical AI reporting and early-stage evaluation;
- AI safety and human oversight.

Bridge sources inform the codebook but are not counted as empirical medical-world-model studies.

## Exclusion Criteria

- Static classifiers, regressors, or risk scores without learned temporal evolution.
- Ordinary sequence models evaluated only on one-step prediction when no rollout or state-transition interpretation is supplied.
- Medical image or text generators without temporal or action-conditioned dynamics.
- Concept papers without empirical evaluation, except in the review-comparison corpus.
- Non-medical world models used only as generic background.
- Records without stable metadata or inspectable primary text.

## Information Sources

The reproducible public search executed on 2026-09-12 covered:

- MEDLINE/PubMed;
- Europe PMC;
- OpenAlex;
- Crossref;
- arXiv public search, using an HTML fallback after the export API returned HTTP 429;
- backward and forward citation searches from included reviews and empirical papers.

Exact-title and identifier checks used official arXiv, CVF Open Access, Springer proceedings, PubMed Central, publisher, and project pages. IEEE Xplore, the ACM Digital Library, Scopus, and Web of Science were not directly queried because authenticated access was unavailable in the execution environment. This limitation must remain explicit unless an author reruns those sources before submission.

## Initial Executed Search Snapshot

- Date range: 2020-01-01 through 2026-09-12.
- Raw records: 9,992.
- Source records: PubMed 77; Europe PMC 1,429; OpenAlex 5,449; Crossref 3,000; arXiv HTML fallback 37.
- Deduplicated records: 5,744.
- Records passing the rerun automated discovery phrase/domain checks: 410.
- Records entering the original database title/abstract screen: 409; one
  additional record had been removed by an invalid publisher policy and was
  subsequently restored through the correction audit.
- Citation-chasing records assessed: 6, of which 2 duplicated the final database set and 4 were unique.
- Original unique title/abstract screening pool: 413, comprising the 409
  database records then retained plus four unique citation-chasing additions.
- Search code: `scripts/search_literature.py`.
- Search log: `screening/search-log.json`.
- Citation audit: `screening/citation-chasing-log.md`.

The automated phrase/domain check was a discovery filter, not an eligibility
decision. The initial two-pass screen, full-text review, and post-extraction
eligibility re-audit produced a **provisional** corpus of 53 records: 50
empirical studies and three reviews. These counts are retained as a reproducible
development snapshot, not as the final review flow.

## Protocol Deviations and Search Correction

The initial discovery implementation required both an explicit world-model
phrase and a medical-domain term in the title or abstract. A stratified audit
of 169 original filter exclusions found potentially eligible records in random
samples from both exclusion strata. The filter therefore failed as a definitive
eligibility rule.

The corrective workflow initiated on 12 September 2026 is:

1. retain the completed 170-record audit, comprising 169 original exclusions
   and one publisher-policy correction;
2. screen 1,030 records from an expanded alternate-terminology search, including
   86 original-search exclusions and 944 records from fresh public searches;
3. independently rescreen all 5,079 residual original-search exclusions not
   covered by steps 1 or 2;
4. conduct duplicate-independent full-text review and third adjudication for
   every record retained by either title/abstract reviewer;
5. merge publication lineages, repeat extraction and MedWM-Eval coding for new
   empirical inclusions, and regenerate every count, table, figure, and
   reference before corpus freeze.

The completed sampled audit initially retained 14 records. A separate
full-text inclusion quality-control pass removed five boundary records. A
source-sufficiency check then removed one conference-abstract-only empirical
record, leaving eight provisional additions (five empirical and three
reviews). The five empirical additions have completed two independent,
source-grounded extraction and MedWM-Eval coding passes. The coding passes
agreed on 91 of 105 decisions (86.67%); all 14 disagreements across four
studies have been source-grounded and adjudicated. Cross-source
publication-lineage adjudication subsequently retained all 40 records absent
from the development snapshot as distinct publications, yielding a corrected
lineage-resolved corpus of 93 publications: 85 empirical studies and eight
reviews. The 40 novel records comprise 35 empirical studies and five reviews.
The remaining 30 novel empirical studies completed independent extraction and
MedWM-Eval coding in three disjoint batches. All 35 novel empirical studies
were source-grounded and adjudicated, and the corrected 85-study analyses,
references, figures, and manuscript were regenerated. Qualified human
verification is still required.

The expanded alternate-term title/abstract screen is complete for all 1,030
records. The two independent reviewers agreed on 926 records (89.90%; Cohen's
kappa 0.5998), and the conservative rule advanced 198 records not excluded by
both reviewers to dual full-text assessment. The full-text reviewers agreed on
157 decisions (79.29%; Cohen's kappa 0.6311), resolving 109 records by
consensus and sending 89 to third-review adjudication. Third review retained 20
and excluded 69, producing a raw pre-QC set of 115 proposed inclusions (98
empirical and 17 reviews). A separate conservative full-text inclusion-QC pass
retained 69 records (67 empirical and two reviews) and excluded 46. Final
conceptual-equivalence and source-sufficiency review excluded 43 adjacent
dynamic-modeling records and retained 26 core
records: 24 empirical studies and two reviews. Cross-source
publication-lineage reconciliation is complete.

The exhaustive residual title/abstract rescreen is complete for all 5,079
records. The two independent reviewers agreed on 5,004 records (98.52%;
Cohen's kappa 0.5472), and the same conservative rule advanced 119 records to
dual full-text assessment. The full-text reviewers agreed on 108 decisions
(90.76%; Cohen's kappa 0.7714), resolving 105 records by consensus and sending
14 records, including corpus-type disagreements, to third-review
adjudication. Third review retained six and excluded eight, producing a raw
pre-QC set of 32 proposed inclusions (30 empirical and two reviews). The
conservative independent inclusion-QC pass retained 18 records (17 empirical
and one review) and excluded 14. Final conceptual-equivalence and
source-sufficiency review excluded 12 adjacent records and retained six
empirical studies. Cross-source publication-lineage reconciliation is
complete.

Human author verification is still required before the process can be
represented as submission-ready dual screening.

The submission search would be strengthened by author reruns of:

- IEEE Xplore;
- ACM Digital Library;
- Scopus or Web of Science;
- official dataset and project pages for access and version verification.

## Search Concept Blocks

The database-specific syntax will combine:

```text
("world model" OR "world-model" OR "latent dynamics" OR
 "action-conditioned model" OR "patient simulator" OR
 "clinical simulator" OR "disease trajectory model" OR
 "medical digital twin")
AND
(medical OR clinical OR patient OR healthcare OR physiological OR
 imaging OR ultrasound OR surgical OR treatment OR intervention)
AND
(trajectory OR rollout OR dynamics OR simulation OR planning OR
 counterfactual OR intervention)
```

The core search will be complemented by title searches for known systems and bridge searches for evaluation methodology. Every database query, field restriction, date, and result count will be stored before screening.

## Screening

1. Deduplicate by DOI, arXiv identifier, normalized title, and publication lineage.
2. Conduct title/abstract screening against the corpus criteria.
3. Conduct full-text screening for dynamic-state and evaluation eligibility.
4. Record one primary exclusion reason for each excluded full text.
5. Use two independent screeners for the submission review.
6. Resolve disagreements through discussion and a third adjudicator when necessary.
7. Report agreement before adjudication and the final PRISMA-ScR flow.

The developmental title/abstract screen contained 413 unique records, of which
344 were excluded and 69 proceeded to full-text assessment. Sixteen full texts
were excluded and 53 records were included. Before adjudication, raw agreement was
95.52% (Cohen's kappa 0.8454) in the initial 402-record title/abstract stratum
and 94.20% (Cohen's kappa 0.8449) at full text. The seven-record arXiv addendum
and six-record citation supplement had 100% agreement but insufficient decision
variation for an informative kappa. These are AI-assisted development results
and must not be represented as completed human dual screening.

## Data Charting

The study-level extraction fields are defined in `extraction-schema.md`. Two reviewers will independently code the fields that affect MedWM-Eval conclusions. Disagreements will be preserved until adjudication rather than silently merged.

## Quality and Bias Appraisal

Because the corpus contains heterogeneous study types, one universal risk-of-bias score would be misleading. Appraisal will use study-type-specific domains:

- retrospective prediction and trajectory studies: cohort construction, leakage, missingness, censoring, calibration, and external validation;
- causal or counterfactual studies: estimand, eligibility, time zero, treatment strategies, confounding, positivity, censoring, and identification;
- clinician or decision-support studies: sampling, comparator, blinding where feasible, outcome validity, and human-factors design;
- embodied control studies: simulator fidelity, action support, closed-loop protocol, safety constraints, and real-system transfer.

The review will report domain-level judgments rather than collapse them into one quality number.

For the corrected final corpus, this plan is implemented in
`final-corpus/analysis/methodological-appraisal.csv` and its JSON/Markdown
summaries. The matrix preserves narrative strengths, limitations, and source
anchors and reports domain-level counts for the study-type-sensitive features
above. It is explicitly descriptive and is not presented as a validated
risk-of-bias instrument.

## Synthesis Plan

1. Describe study characteristics and publication status.
2. Report counts and proportions for each extracted evaluation feature.
3. Separate findings by capability claim and domain track.
4. Distinguish:
   - evidence observed in included studies;
   - principles imported from bridge methodology;
   - new author recommendations.
5. Compare the proposed codebook with the three existing medical-world-model reviews.
6. Pilot the MedWM-Eval codebook on the complete empirical corpus.
7. Report inter-rater agreement and adjudicated disagreements.
8. Avoid meta-analysis when tasks, outcomes, and metrics are not commensurable.

## Planned Artifacts

- PRISMA-ScR flow diagram.
- Full search log.
- Included and excluded study list with reasons.
- Study-level evidence matrix.
- Existing-review comparison matrix.
- Capability × evidence matrix.
- Dataset task cards.
- MedWM-Eval codebook and pilot-coding results.
