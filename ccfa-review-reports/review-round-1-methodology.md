# Peer Review Report 1: Methodology

**Manuscript:** *Evaluating Medical World Models: A Scoping Evidence Map of Rollout, Causal Validity, and Safety*  
**Reviewer role:** Peer Reviewer 1, Methodology  
**Review round:** First round  
**Recommendation:** Major revision; not suitable for submission in its current developmental state  
**Confidence:** High  
**Calibration status:** `NOT_CALIBRATED`  
**Venue note:** Journal of Biomedical Informatics is provisional. Journal-specific formatting or acceptance criteria were not applied because no verified, binding venue instructions were provided.

## Overall assessment

This is a timely, potentially valuable evaluation-centred review. Its main strengths are the unusually transparent evidence artifacts, capability-specific interpretation, explicit separation of reported evidence from demonstrated capability, and mostly accurate numerical synthesis.

However, two issues currently prevent publication: the evidence selection and extraction remain AI-assisted developmental work without completed human verification, and the executed search is substantially narrower than the stated search strategy. The citation-chasing audit already demonstrates that eligible studies can be missed by the mandatory “world model” phrase filter. These problems affect the validity of the corpus, not merely reporting quality.

## Genuine strengths

1. **Strong auditability.** The project preserves included and excluded records, extraction fields, dual coding, disagreements, adjudication notes, search counts, and re-audit corrections.

2. **Accurate core arithmetic.** The final artifacts consistently contain 50 empirical studies and three reviews. The capability counts and most evidence counts in the manuscript reproduce the final CSV. The agreement calculation is also correct: 976/1,050 = 92.95%, with 74 disagreements across 37 studies.

3. **Appropriate avoidance of an aggregate score.** MedWM-Eval does not sum heterogeneous evidence domains into a potentially misleading quality rank.

4. **Conceptually important distinctions.** The separation among passive forecasting, action conditioning, counterfactual comparison, and planning is useful. The discussion of observation fidelity versus transition, causal, and decision validity is particularly strong.

5. **Clear figures.** Both figures are legible and professionally composed. Figure 2 clearly distinguishes offline, simulated, and real-system evaluation.

## Critical issues

### C1. The review process is not yet complete

The manuscript acknowledges that screening, extraction, and coding remain AI-assisted developmental artifacts and that human verification is pending (Methods §2.3; Limitations; Figure 1 footer).

This is not simply a limitation. Until humans verify eligibility, exclusions, extraction, and material coding decisions, the corpus and conclusions cannot be treated as a completed scholarly scoping review.

**Required revision:** Conduct independent human verification of every inclusion and full-text exclusion, dual verification of synthesis-determining fields, adjudication by a third qualified reviewer, and regenerate all counts, statistics, figures, and conclusions.

### C2. The search cannot currently support a comprehensive evidence map

The manuscript says queries combined world-model terms with trajectory, rollout, simulation, intervention, and planning concepts (Methods §2.2). The executed search instead required the literal phrase “world model” or a close spelling variant. The automated filter excluded 4,956 records because that phrase was absent.

This filter has demonstrated false negatives: citation chasing found eligible EchoJEPA and treatment-aware diffusion work specifically because their titles did not use “world model.”

Coverage is further constrained by:

- OpenAlex truncation at 1,000 records for several queries.
- Crossref retrieval of only 250 ranked records per extremely broad query.
- No direct IEEE Xplore, ACM Digital Library, Scopus, or Web of Science search.
- A publisher-based MDPI exclusion rather than a study-methodology criterion.

**Required revision:** Execute database-specific searches covering latent dynamics, patient simulators, digital twins, action-conditioned models, disease trajectories, and model-based control without requiring self-identification as a world model. Search the missing specialist databases, remove publisher-level exclusion, validate the discovery filter against a random excluded sample, and rerun screening.

## Major issues

### M1. Eligibility boundaries remain unstable

The corpus includes peripheral or borderline records such as affective music recommendation, nonclinical emotional physiology, radiologist gaze modelling, masked representation learning, and single-query future prediction. These may be defensible under a broad definition, but they do not consistently represent clinical or biological state evolution.

Meanwhile, some excluded studies used learned predictive dynamics but lacked a specific form of direct evaluation. The distinction between “medical world model,” “health-related sequential model,” and “adjacent methodology” therefore remains partly dependent on author terminology.

**Required revision:** Define a strict core corpus and an extended peripheral corpus. Report a sensitivity analysis excluding borderline studies and determine whether the headline gaps change.

### M2. The post-extraction re-audit needs a complete, chronological audit trail

The original extraction and coding contained 55 empirical studies; the final corpus contains 50. The re-audit occurred after extraction and MedWM-Eval coding, but the final re-audit file records only the six removed records, not retained-study decisions.

The manuscript should establish:

- Whether auditors were blinded to MedWM-Eval results.
- Whether all provisional inclusions received documented decisions.
- Why agreement is reported only for the post-re-audit 50-study subset.
- How the original 55-study agreement differed.
- Which artifact version is authoritative at each stage.

**Required revision:** Preserve all retain and exclude decisions with evidence anchors, disclose the chronology and blinding conditions, and report both pre- and post-re-audit agreement results or justify the selected analysis population.

### M3. MedWM-Eval has reliability evidence, but not validity evidence

The rubric is explicitly developmental. It has not undergone human content validation, construct validation, specialty review, or external replication.

Several rules also mix applicability and absence. For example, safety is described as scope-dependent in the capability matrix, but all 50 studies receive a safety score, potentially classifying irrelevant safety evaluation as missing. External validation is similarly scored for every study although the matrix requires it primarily for transport claims.

The “highest claim anywhere in the manuscript” rule may classify aspirational or rhetorical language as the study’s operating claim.

**Required revision:** Obtain structured review from clinical, causal-inference, embodied-control, and measurement experts. Define claim hierarchy, applicability rules, and handling of aspirational language before presenting MedWM-Eval as more than a preliminary instrument.

### M4. Agreement statistics are incomplete

Unweighted Cohen’s kappa is reported for ordinal 0/1/2 domains. Weighted kappa would better distinguish adjacent from extreme disagreement. The pooled 92.95% agreement combines 21 heterogeneous fields and is dominated by common or easier decisions.

No uncertainty intervals are reported, and “independent coders” is insufficiently reproducible without model/version, prompt, temperature, evidence access, and independence details.

**Required revision:** Report per-field raw agreement, weighted kappa for ordinal fields, nominal kappa for categorical fields, and study-level bootstrap confidence intervals. Treat AI agreement as process reproducibility, not instrument validity.

### M5. The planned quality appraisal was not fully implemented

The protocol specifies study-type-specific appraisal of leakage, missingness, censoring, causal identification, simulator fidelity, human factors, and physical safety. The extraction contains narrative strengths and limitations, but the manuscript does not provide a structured risk-of-bias or methodological-quality synthesis.

Because 40 of 50 empirical studies are preprints or unreviewed, equal contribution to headline counts warrants sensitivity analysis.

**Required revision:** Complete the planned domain-level appraisal or formally amend and justify the protocol. Report sensitivity analyses by publication status and methodological quality.

### M6. The central mismatch claim needs direct cross-tabulation

Figure 2 presents marginal capability and evidence counts, not the capability-by-required-evidence matrix implied by the paper’s central contribution. Readers cannot directly see, for example, how many planning studies satisfied rollout, calibration, external-validation, decision, and safety requirements simultaneously.

**Required revision:** Add capability × evidence tables and publication-status sensitivity analyses. Replace the temporal claim that the field is “advancing faster than its evaluation,” because no longitudinal trend analysis was performed.

### M7. Section 5 contains an under-reported original experiment

The PhysioNet benchmark and sanity-baseline findings in §5 are new empirical results, but the manuscript supplies no complete experimental methods, split definitions, statistical procedures, or result table.

For a review-first workflow, these results should move to the planned original research paper. Alternatively, they require full methods and reporting here.

**Required revision:** Remove the baseline results from the review and reserve them for the original research paper, or add a complete empirical methods and results section appropriate to an original investigation.

## Minor issues

### m1. Review design terminology

The title and reporting framework describe a scoping review, while the manuscript labels the article a methodological review. State explicitly whether this is a scoping review that develops a methodological instrument, a methodological review with a scoping search, or a hybrid design, and apply the corresponding reporting standard consistently.

### m2. Coding terminology

The 1,050 coding observations are study-field decisions rather than independent “claim-level” observations. Revise the terminology so the statistical unit is unambiguous.

### m3. Reporting of unclear evidence

Use a consistent convention for `unclear`, `NI`, and `NA` values in text, tables, figures, and percentages. Do not silently remove unclear observations from denominators.

### m4. Availability statement

Ensure that the final supplementary package contains the complete re-audit decisions, exact search inputs, model and prompt provenance, software versions, and authoritative post-re-audit extraction audit promised by the Data, Code, and Materials Availability section.

## Numerical and figure checks

### N1. Figure 1 has an unexplained arithmetic transition

5,744 − 5,335 = 409, but the next box reports 413. Add the four unique citation-chasing records as a separate input.

### N2. Figure 1 does not display the final re-audit

The caption states that the figure shows the final eligibility re-audit, but the visual contains no explicit re-audit stage. It should also report the full-text exclusion distribution:

- Inaccessible full text: 5.
- No future or action evaluation: 4.
- No primary empirical evaluation: 3.
- No learned dynamics: 3.
- Review not primarily about medical world models: 1.

### N3. Denominators are inconsistent

Figure 2 reports frozen external validation as 9/50 and public code as 18/50. The final summary reports 9/47 and 18/30 after removing unclear cases. Select one denominator convention and explicitly display unclear observations.

### N4. Inaccessible-record count requires clarification

The limitations report four inaccessible records, whereas the final excluded corpus contains five. Clarify that four were post-extraction corrections but five were excluded for inaccessible full text overall.

### N5. Verified consistent quantities

The following final-corpus quantities are internally consistent:

- 53 included records: 50 empirical studies and three reviews.
- Capability claims: planning 19, action-conditioned 15, counterfactual nine, passive forecasting seven.
- Free-running rollout 28 and horizon-resolved results 23.
- Formal calibration four, frozen external validation nine, and safety-hazard testing 11.
- Closed-loop setting: no closed loop 27, offline 13, simulation six, real system four.
- 1,050 coding decisions, 976 agreements, 74 disagreements, and 37 studies with at least one disagreement.

## Criterion-bound judgements

| Criterion | Judgement |
| --- | --- |
| Review question and importance | Met |
| Search sensitivity and coverage | Not met |
| Eligibility consistency | Partially met |
| Screening validity | Not met pending human verification |
| Extraction completeness | Structurally met; substantive verification pending |
| Post-extraction re-audit | Partially met |
| Coding-instrument validity | Not met |
| Coding reliability reporting | Partially met |
| Numerical consistency | Mostly met, with denominator and flow corrections |
| Evidence synthesis | Partially met |
| Reproducibility | Partially met |
| Conclusions supported by evidence | Partially met |
| AI-process disclosure | Met |
| Figure clarity | Met |
| Figure methodological completeness | Partially met |

## Questions for the authors

1. Were the two AI coding passes performed using different models or genuinely independent contexts, and were coders blinded to one another and to final eligibility decisions?

2. Was the post-extraction eligibility re-audit blinded to MedWM-Eval scores, and why are retained-study audit decisions not preserved alongside the six exclusions?

3. Is the target corpus intended to include every medical learned-dynamics model, or only studies explicitly framed as world models? How will the revised search operationalize this distinction?

4. How were the 17 causal-applicable studies determined, and why are safety and external-validity domains scored as absent for studies where those domains may be inapplicable?

## Decision

**Major revision.** The conceptual contribution is promising, but a submission should wait for a broader search, completed human verification, validated applicability rules, and a fully versioned audit trail.
