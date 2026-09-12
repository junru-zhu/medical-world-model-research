# Scientific and Publication Review

## Current Independent Review — Round 4

**Review date:** 12 September 2026  
**Recommendation:** Major revision  
**Overall score:** 6/10 from both independent reviewers  
**Confidence:** 4.5/5 and high confidence  
**Manuscript:** *Capability-Matched Evaluation of Medical World Models: A Scoping Review of Rollout, Causal Validity, and Safety*

### Current assessment

The review has a publishable premise and a technically coherent evidence
package. Its distinctive contribution is a study-level, capability-matched
audit rather than another architecture taxonomy. The corrected,
lineage-resolved corpus contains 85 empirical publications and eight reviews;
the revised main analysis uses 82 directly clinical or biomedical studies,
with three health-adjacent records retained only as boundary sensitivity.

The manuscript is not submission-ready. Qualified human dual verification,
expert content validation, authenticated engineering/citation-database
searches, information-specialist review, healthcare-professional involvement,
human spot-checking of the completed metadata audit, stable artifact
deposition, and final author declarations remain open.

### Convergent strengths

- Clear separation of passive forecasting, action-conditioned simulation,
  counterfactual comparison, and planning.
- Strong restraint around action responsiveness versus causal treatment
  effects.
- Explicit study-level denominators, source anchors, sensitivity analyses, and
  reproducible technical artifacts.
- Professional visual communication and a useful claim-to-evidence framework.
- Defensible novelty as operational evidence accounting, especially the joint
  evidence intersections, rather than a new capability ladder.

### Major findings and revision status

| ID | Reviewer finding | Revision status |
| --- | --- | --- |
| R4-01 | Human validation and authenticated search coverage remain incomplete | Open submission gate; cannot be repaired by wording |
| R4-02 | Calibration prevalence used a corpus-wide denominator without an applicability sensitivity | Resolved: 5/82 is explicitly labeled reporting prevalence and 5/37 is reported among studies with partial or direct uncertainty evidence |
| R4-03 | Highest-capability and causal/policy applicability rules were insufficiently operational | Resolved: a fixed tie-break order, nonexclusive tracks, the 35-study causal/policy denominator, and candidate-level provenance are documented |
| R4-04 | MedWM-Eval recommendations sounded more validated or mandatory than the evidence permits | Resolved: the framework is consistently labeled preliminary and normative terms were softened to recommendations or considerations |
| R4-05 | Benchmark selection was not sufficiently auditable | Resolved: Table 4 compares candidate gaps by recurrence, clinical relevance, accessible-data feasibility, measurability, and overclaim risk |
| R4-06 | Simulator/model-mismatch safety could be mistaken for an extracted prevalence feature | Resolved: the manuscript states that mismatch was not separately counted and labels the corresponding material as framework guidance |
| R4-07 | Sensitivity reporting did not show whether the main gap survived alternate corpus definitions | Resolved: explicit-world-model and high-confidence subsets are reported; the peer-reviewed and domain sensitivities remain visible |
| R4-08 | Fifteen frozen-validation flags and thirteen directly auditable external-evidence ratings appeared inconsistent | Resolved: the manuscript distinguishes the binary confirmed feature from the stricter ordinal evidence rating |
| R4-09 | Reference verification and the final dataset-reference year were incomplete | Substantially resolved: all 99 entries underwent an independent metadata audit and reference 99 now includes 2019; human spot checking remains pending |
| R4-10 | PRISMA and standing review-status artifacts were stale | Resolved: both were updated after final corpus regeneration and technical validation |

### Current quantitative basis

- Primary corpus: 82 clinical/biomedical empirical studies.
- Highest capability claimed: planning 33, action-conditioned simulation 22,
  counterfactual comparison 18, passive forecasting 9.
- Free-running rollout 54/82; horizon-resolved results 41/82; formal
  calibration 5/82; confirmed frozen external validation 15/82; explicit
  safety-hazard test 20/82.
- Joint evidence: rollout+horizon+calibration 2/82;
  rollout+horizon+external validation 4/82; all four criteria 0/82.
- Action tests: comparator 30/72 and perturbation 45/72 among studies with an
  operational action input.
- Explicit causal estimand: 12/35 causal or policy-applicable studies.
- Calibration sensitivity: 5/37 among studies with partial or directly
  auditable uncertainty evidence.
- Technical package validation: pass; abstract 337 words, body 5,509 words,
  five tables, three figures, and 99 linked references.

### Decision conditions

The paper can move toward minor revision only after:

1. authenticated database updates and information-specialist review;
2. qualified human verification of screening, extraction, coding, and
   adjudication;
3. multidisciplinary content validation and a human reliability pilot for
   MedWM-Eval;
4. human spot-checking of the completed DOI/publisher metadata audit;
5. stable, versioned artifact deposition;
6. final author, funding, competing-interest, CRediT, and
   healthcare-professional statements.

The material below is the archived earlier-round review and is retained only
for revision provenance.

## 1. Review Information

- **Manuscript:** *Evaluating Medical World Models: Datasets, Metrics, Causal Validity, and Safety Across Clinical and Embodied Systems*
- **Article type:** Methodological review with planned scoping-review update
- **Target venue:** Journal of Biomedical Informatics
- **Review date:** 12 September 2026
- **Review mode:** Full scientific, methodological, writing, and publication-readiness review
- **Reviewers:** Two independent review calls
- **Materials inspected:** Revised manuscript, full-text 12-study matrix, protocol, extraction schema, codebook, dataset task cards, venue plan, and bibliography
- **Round:** 2

## 2. Expected Review Outcome

**Current stance: major revision; not submission-ready.**

The manuscript has a publishable evaluation-centered premise, a coherent structure, sound causal instincts, and a completed first-pass extraction of twelve empirical studies. The remaining decisive weakness is that the reproducible scoping review has been designed but not executed. The search corpus is not frozen, dual screening and quality appraisal are absent, and the MedWM-Eval codebook has not been independently piloted.

The writing itself is not the main blocker. Both reviewers judged the architecture and prose favorably. Publication readiness depends on converting the conceptual synthesis into an auditable evidence product.

## 3. Desk and Reviewability Assessment

| Check | Status | Assessment |
| --- | --- | --- |
| Topic importance | Pass | Evaluation validity for medical world models is timely and clinically consequential. |
| Review identity | Concern | The reviewed version was a targeted structured synthesis rather than a reproducible scoping review. |
| Novelty | Concern | Three broad reviews already cover capability levels, state–dynamics–action structure, causal identifiability, uncertainty, and translation. |
| Evidence traceability | Pass for targeted corpus | A full-text 12-study matrix now supports explicit denominators. |
| Framework auditability | Concern | A codebook and applicability rules exist, but pilot coding and agreement analysis are absent. |
| Target-venue fit | Pass provisionally | Journal of Biomedical Informatics methodological review is a strong fit; final compliance remains open. |
| Bibliographic completeness | Partial | Core metadata were present but required normalization and current-version checks. |
| Ethics and safety | Concern | Safety coverage was too brief relative to the title and intended clinical use. |

## 4. Summary and Contributions

The manuscript asks what evidence is needed to justify four classes of medical-world-model claims:

1. passive forecasting;
2. action-conditioned simulation;
3. counterfactual comparison; and
4. closed-loop planning.

It organizes evidence around state validity, transition validity, rollout stability, action semantics, uncertainty, causal interpretation, external validity, decision utility, and safety. The potentially distinctive contribution is not the capability ladder itself. It is an operational capability × regime × evidence matrix, dataset task cards, and a reproducible MedWM-Eval codebook.

## 5. Strengths

### STRENGTH-01: Correct causal boundary

The manuscript distinguishes conditioning on recorded treatment from identifying a treatment effect. This is essential because generative responsiveness to an action token does not validate an unobserved patient-specific outcome.

### STRENGTH-02: Evaluation-centered framing

Teacher-forced versus free-running rollout, horizon degradation, action sensitivity, calibration, external validation, and decision utility form a useful evidence hierarchy.

### STRENGTH-03: Strong manuscript architecture

The progression from definition to capability levels, empirical domains, evaluation dimensions, datasets, reporting, and research agenda is readable and logically ordered.

### STRENGTH-04: Appropriate cross-domain caution

The manuscript does not force EHR, imaging, ultrasound, and robotic-control systems into one universal leaderboard.

### STRENGTH-05: Transparent draft status

The manuscript states that the search and extraction are incomplete. It does not represent a targeted search as a completed systematic review.

## 6. Major Concerns

### REV-01 — The review method is not yet reproducible

- **Severity:** Critical
- **Location:** Review Scope and Method
- **Evidence:** Search platforms and broad terms were reported, but database-specific strings, result counts, deduplication, screening, exclusions, charting, and synthesis were incomplete.
- **Consequence:** Independent readers cannot reproduce the corpus or determine selection bias.
- **Resolution condition:** Complete a PRISMA-ScR-compatible search and flow with dual screening, full-text exclusions, and a frozen extraction protocol.

### REV-02 — Novelty relative to existing reviews remains exposed

- **Severity:** Critical
- **Location:** Introduction, capability ladder, and framework
- **Evidence:** Existing reviews already provide capability levels and broad discussions of action semantics, uncertainty, causal identifiability, long-horizon error, external validation, and safety.
- **Consequence:** A prose taxonomy or checklist can be interpreted as repackaging.
- **Resolution condition:** Add a criterion-level review comparison and deliver an operational artifact absent from the existing reviews.

### REV-03 — Synthesis claims lack study-level denominators

- **Severity:** Critical
- **Location:** Abstract, empirical synthesis, and conclusion
- **Evidence:** The reviewed version did not show which studies evaluated calibration, free-running rollout, external validation, causal assumptions, or decision utility.
- **Consequence:** Statements about field-wide fragmentation are plausible but not auditable.
- **Resolution condition:** Complete full-text extraction and report counts such as the number and proportion of studies satisfying each criterion.

### REV-04 — MedWM-Eval was a taxonomy rather than an executable framework

- **Severity:** Major
- **Location:** Framework and checklist
- **Evidence:** Metric definitions, applicability rules, coding values, task specifications, failure criteria, and pilot application were absent.
- **Consequence:** Claims of comparability and auditability exceeded the artifact.
- **Resolution condition:** Publish a codebook, dual-code the corpus, report agreement and adjudication, and separate required from optional criteria by capability track.

### REV-05 — Causal and longitudinal protocols need formalization

- **Severity:** Major
- **Location:** Counterfactual comparison and causal validity
- **Evidence:** Observed-policy prediction, population intervention effects, dynamic-regime value, and individual counterfactual trajectories were not formally separated. Informative observation, irregular sampling, censoring, competing events, care-policy leakage, and stochastic rollout replication were underdeveloped.
- **Consequence:** The framework can endorse invalid tests or overinterpret observational conditioning.
- **Resolution condition:** Define estimands and domain-specific protocols, including eligibility, time zero, treatment strategies, horizon, outcome, confounding, positivity, censoring, and validation target.

### REV-06 — Dataset fitness judgments were insufficiently operational

- **Severity:** Major
- **Location:** Dataset Fitness
- **Evidence:** Dataset recommendations were not scored against action provenance, temporal density, missingness, outcomes, censoring, harmonization, safety-event prevalence, and access.
- **Consequence:** A dataset can appear suitable while lacking support for the intended causal or planning claim.
- **Resolution condition:** Replace general recommendations with cited dataset task cards and explicit permissible-claim boundaries.

### REV-07 — Safety evidence is too thin

- **Severity:** Major
- **Location:** Decision utility and safety; reporting checklist
- **Evidence:** The reviewed version did not fully address hazard severity, simulator exploitation, subgroup worst cases, automation bias, human override, monitoring, model updates, incident response, privacy, or responsibility allocation.
- **Consequence:** Safety in the title and contribution is not matched by the synthesis.
- **Resolution condition:** Add separate safety protocols for clinical decision support and embodied control.

### REV-08 — The world-model boundary and bridge literature need strengthening

- **Severity:** Major
- **Location:** Inclusion criteria and definition
- **Evidence:** The definition could admit ordinary autoregressive prediction while excluding adjacent causal, digital-twin, calibration, and control literature needed to justify evaluation recommendations.
- **Consequence:** The corpus boundary appears label-driven.
- **Resolution condition:** State necessary and sufficient core-corpus criteria and add a separate bridge-methodology corpus.

### REV-09 — Visual evidence and venue adaptation are missing

- **Severity:** Moderate
- **Location:** Whole manuscript
- **Evidence:** The capability ladder, evaluation cube, review comparison, evidence matrix, and dataset task cards were not visualized.
- **Consequence:** The taxonomic contribution remains difficult to inspect.
- **Resolution condition:** Add the review flow, existing-review comparison, study matrix, capability × evidence matrix, codebook derivation, and expanded dataset table after venue limits are known.

## 7. Minor and Presentation Concerns

- The title's “long-horizon clinical simulation” does not naturally cover short-horizon ultrasound navigation and surgical control. Broaden the title or define horizon by domain.
- Preprint and peer-reviewed status should be visible in the empirical study matrix.
- Final references require one consistent venue style and a last-cutoff metadata audit.
- Normative terms such as “must,” “minimum,” and “requires” should distinguish reviewed evidence, imported methodology, and author proposals.

## 8. Novelty and Positioning

| Work | Existing contribution | Remaining defensible difference | Consequence |
| --- | --- | --- | --- |
| Qazi et al., 2025 | Capability levels from clinical prediction to planning | No operational study-level evaluation codebook identified in the reviewed comparison | The ladder alone is not novel |
| Liu et al., 2026 | State, dynamics, and intervention-policy roadmap | Evaluation is not the sole organizing axis | Architecture-level framing is already covered |
| Chen et al., 2026 | Broad structured synthesis with 98 sources and 14 strict empirical studies | A validated claim-to-evidence matrix may remain distinct | Highest novelty risk |
| Current manuscript | Evaluation dimensions, dataset fitness, and MedWM-Eval proposal | Distinct only when operationalized and piloted | Publication route is benchmark and audit methodology |

## 9. Soundness and Claim Support

| Claim | Reviewed support | Judgment | Action |
| --- | --- | --- | --- |
| Evaluation is fragmented | Qualitative examples from a targeted corpus | Plausible, not yet quantified | Complete extraction and report denominators |
| Action conditioning is not causal identification | Causal logic and supporting methodology | Sound | Formalize estimand-specific tracks |
| One aggregate metric cannot compare all domains | Heterogeneous tasks and outputs | Sound | Preserve domain-specific tracks |
| MedWM-Eval makes studies comparable | Preliminary prose taxonomy in reviewed version | Overstated | Pilot codebook and report coding reliability |
| MIMIC-IV plus eICU is the strongest benchmark route | Author judgment without full task-card comparison | Unsupported as written | Score datasets under explicit criteria |

## 10. Evaluation and Reproducibility

The decisive missing evidence is review evidence rather than a new model experiment:

- reproducible search and screening;
- complete full-text extraction;
- study-type-specific quality appraisal;
- codebook and pilot coding;
- agreement and adjudication;
- current data/code/access verification;
- traceable synthesis counts.

## 11. Independent Reviewer Perspectives and Synthesis

| Reviewer | Lens | Stance | Main positive signal | Main negative signal |
| --- | --- | --- | --- | --- |
| Reviewer A | Scientific validity, causal interpretation, safety, dataset fitness | Major revision; 4/10 | Correct causal boundaries and useful evaluation dimensions | Claims and framework exceed extracted evidence |
| Reviewer B | Review methodology, positioning, writing, publication readiness | Major revision; readiness 2/5 | Strong organizing problem and professional structure | Search, extraction, and framework derivation are not reproducible |

**Agreement:** Both reviewers identified incomplete evidence extraction and weak differentiation from existing reviews as the decisive blockers. Both considered the prose and organizing idea strengths.

**Final calibrated stance:** Major revision. The publishable contribution is an auditable evaluation-methodology review, not another general survey.

## 12. Critical Reviewer Ratings

| Dimension | Score (1–5) | Confidence | Basis | Score-change condition |
| --- | ---: | ---: | --- | --- |
| Novelty | 2 | 4 | Strong overlap with three reviews | Operational crosswalk, codebook, and pilot |
| Soundness | 3 | 4 | Causal instincts are sound; protocols incomplete | Formal causal and longitudinal tracks |
| Evidence | 2 | 4 | Targeted corpus without full extraction | Quantified study matrix |
| Significance | 4 | 4 | Important evaluation problem | Preserve focused contribution |
| Clarity | 4 | 4 | Coherent manuscript architecture | Add inspectable figures and matrices |
| Reproducibility | 1 | 5 | Search and coding not reproducible | PRISMA-ScR search, schema, dual coding |
| Ethics and safety | 3 | 4 | Safety recognized but underdeveloped | Deployment-specific safety synthesis |

**Overall:** 5/10  
**Recommendation:** Major revision  
**Confidence:** 4/5

## 13. Decision Conditions

- **Raise to 6/10:** Execute and freeze the PRISMA-ScR search, dual screening, exclusion log, and flow.
- **Raise novelty to 4/5:** Deliver a criterion-level crosswalk and an operational artifact absent from existing reviews.
- **Raise reproducibility to 4/5:** Release the protocol, extraction schema, codebook, task cards, and dual-coding results.
- **Reach 7–8/10:** Pilot MedWM-Eval on the complete corpus and show that it produces reliable, decision-relevant distinctions.
- **Exceed 8/10:** Validate the framework independently or instantiate it as a real-data benchmark that materially changes model conclusions or rankings.

## 14. Action Priorities and Re-Review Status

| ID | Priority | Required change | Current status |
| --- | --- | --- | --- |
| REV-01 | Critical | Freeze and execute PRISMA-ScR protocol | Protocol drafted; execution open |
| REV-02 | Critical | Compare against all three reviews | Comparison table added; evidence crosswalk open |
| REV-03 | Critical | Complete study-level extraction | Fixed for current 12-study corpus; final corpus pending |
| REV-04 | Major | Create and pilot MedWM-Eval codebook | Preliminary codebook created; pilot open |
| REV-05 | Major | Formalize causal and longitudinal tracks | Partially addressed; detailed protocols open |
| REV-06 | Major | Create dataset task cards | Preliminary task cards created; verification open |
| REV-07 | Major | Expand safety analysis | Codebook expanded; manuscript synthesis open |
| REV-08 | Major | Add bridge-methodology corpus | Initial reporting and causal sources added; broader search open |
| REV-09 | Moderate | Add figures and tables | Two core tables added; graphical abstract and framework figures open |
