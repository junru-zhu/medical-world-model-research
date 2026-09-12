# Peer Review Report: Reviewer 2

**Reviewer role:** Domain and Journal Fit  
**Review date:** 12 September 2026  
**Manuscript:** *Evaluating Medical World Models: A Scoping Evidence Map of Rollout, Causal Validity, and Safety*  
**Target:** Journal of Biomedical Informatics, Methodological Review  
**Round:** First review  
**Calibration status:** `NOT_CALIBRATED`  
**Recommendation:** **Reject and resubmit after completing the review methodology**  
**Confidence:** High for manuscript consistency and journal fit; moderate for individual study classifications because I did not independently reread all 50 primary papers.

## 1. Review Scope and Materials

This was a read-only review. Materials inspected:

- `manuscript/review.md`;
- final-corpus included and excluded records;
- final-corpus study extraction and MedWM-Eval synthesis;
- screening protocol, eligibility summary, and final eligibility re-audit;
- `existing-review-comparison.md`;
- `submission/venue-plan.md`;
- Figure 1 in PNG, SVG, and PDF form;
- Figure 2 in PNG, SVG, and PDF form.

No formal criteria-binding manifest was available for the Journal of Biomedical Informatics. Journal-fit and submission-format comments are therefore advisory. The manuscript's current article type is nevertheless thematically consistent with a methodological review that critically examines the uses, successes, limitations, inappropriate-use conditions, and future directions of a biomedical informatics method.

## 2. Overall Assessment

This is a timely, potentially important methodological review. Its strongest contribution is not another taxonomy of medical world models, but the attempt to audit whether evidence matches the capability claimed. The distinction among passive forecasting, action-conditioned simulation, counterfactual comparison, and planning is useful for biomedical informatics readers.

The manuscript is not publication-ready because its central evidence base remains developmental. Human screening and extraction verification are explicitly pending, major engineering databases were not directly searched, and a large automated discovery filter lacks a reported sensitivity audit. These are not ordinary limitations; they affect the validity and final composition of the corpus.

The provisional JBI fit is good. The manuscript critically examines the use, limitations, and inappropriate interpretation of an informatics method class. The main obstacle is completion and validation of the review methodology, not topic relevance.

## 3. Genuine Strengths

1. **Important conceptual problem.** The manuscript correctly recognizes that image fidelity, one-step prediction, simulator return, causal validity, and clinical utility are different evidentiary claims.

2. **Operational rather than purely taxonomic contribution.** MedWM-Eval asks what evidence supports the highest capability claimed and avoids summing heterogeneous evidence into a misleading universal quality score.

3. **Useful operating-regime distinctions.** Results §§3.2–3.4 distinguish teacher-forced versus free-running rollout and offline, simulated, and real-system closed loops. These distinctions are often blurred in this literature.

4. **Strong causal framing.** §§3.3 and 4.3 clearly explain why action conditioning or reconstruction of factual outcomes does not identify an unobserved treatment effect.

5. **Promising domain-specific synthesis.** §3.5 distinguishes informative observation processes in EHRs, visual versus biological validity in imaging, and physical validity in procedural systems.

6. **Transparent reporting.** The manuscript openly discloses AI assistance, unavailable databases, source-quality limitations, and the human-verification requirement.

7. **Clear figures.** Both figures are legible, visually restrained, and internally consistent with the corrected 50-study corpus.

## 4. Critical Issues

### CR-1: The central review evidence has not received submission-level human verification

**Anchor:** Methods §§2.3–2.4; Limitations §7; Figure 1 footer.

The manuscript states that screening, extraction, capability assignment, disagreement resolution, and evidence coding were AI-assisted and that human verification remains pending. The reported kappas measure agreement between AI-assisted passes, not reliability among trained human biomedical or methodological reviewers.

Because every main result depends on these decisions, the current counts must be considered provisional. Disclosure does not resolve the validity problem.

**Required revisions:**

- Complete independent human verification of all inclusions and full-text exclusions.
- Human-check capability claims and all evidence domains driving headline results.
- Double-extract at least all causal, planning, safety, low-confidence, and boundary studies.
- Report human agreement and adjudication separately from developmental AI agreement.
- Regenerate the corpus, figures, tables, abstract, and conclusions after verification.

### CR-2: Search completeness and the automated discovery filter are not yet defensible for a final evidence map

**Anchor:** Methods §2.2; Figure 1.

The search omitted direct IEEE Xplore, ACM Digital Library, Scopus, and Web of Science querying. This is particularly consequential because the corpus contains substantial medical imaging, robotics, control, and engineering research.

More importantly, 5,335 of 5,744 deduplicated records were removed by an automated phrase/domain filter before eligibility screening. No sentinel-paper recall test, random audit of excluded records, or sensitivity analysis is reported.

**Required revisions:**

- Rerun appropriate engineering and citation-index databases.
- Publish complete source-specific queries and dates.
- Validate the automated filter against known eligible studies.
- Human-screen a stratified random sample of filter exclusions.
- Report estimated false-negative risk or remove the filter from the final workflow.

## 5. Major Issues

### M-1: The operational definition is too broad and produces unstable corpus boundaries

**Anchor:** Abstract Objective; Introduction §§1–2; eligibility criteria in §2.1.

The definition can include almost any temporally conditioned predictor or simulator. Boundary inclusions include affective music recommendation, nonclinical WESAD emotional dynamics, radiologist gaze modeling, vocal-tract representation learning, a legacy malaria simulator, and a dataset paper containing one world-model experiment.

These may be defensible individually, but their inclusion changes capability counts and the apparent maturity of "medical world models."

**Required revisions:**

- Define necessary distinctions from ordinary sequence forecasting, state-space models, digital twins, static perturbation models, representation learning, and general health or wellness systems.
- Report sensitivity analyses for explicitly self-identified world models versus reviewer-inferred world models.
- Report sensitivity analyses for strictly clinical or biomedical studies versus wellness or nonclinical physiological studies.
- Report peer-reviewed versus preprint or unreviewed results.
- Separate core model papers from dataset or benchmark papers.

### M-2: "Highest capability claim" may capture rhetorical ambition rather than the study's empirical claim

**Anchor:** Methods §2.4 and the MedWM-Eval applicability rule.

A capability is assigned from any statement in the title, abstract, introduction, results, or conclusion. This risks treating future work, motivation, or aspirational clinical language as an empirical claim. The resulting claim-evidence mismatch may therefore be partly produced by the coding rule.

**Required revisions:**

- Distinguish demonstrated empirical claims, explicit headline claims, proposed future capabilities, and contextual motivation.
- Provide claim quotations and section anchors in the supplement.
- Recalculate the main analysis using central empirical claims only.
- Obtain human specialist assessment of construct validity; kappa alone is insufficient.

### M-3: Source quality and methodological quality are insufficiently integrated into the synthesis

**Anchor:** Results §§3.1 and 3.5–3.6.

Forty of 50 studies are described as preprints or unreviewed drafts, yet each study contributes equally to descriptive counts. Some records are particularly fragile, including an unreviewed Zenodo Markdown draft without executable artifacts and studies with acknowledged inconsistencies.

MedWM-Eval measures reported evidence completeness, not risk of bias or credibility. These concepts should not be conflated.

**Required revisions:**

- Add a structured study-characteristics table.
- Separate publication status, source quality, cohort design, validation type, and study domain.
- Apply study-type-appropriate methodological appraisal.
- Repeat headline analyses after excluding unreviewed and low-confidence records.
- Discuss whether conclusions are robust to these exclusions.

### M-4: Domain-specific synthesis is conceptually good but empirically underdeveloped

**Anchor:** Results §3.5.

The EHR, imaging, biological, and procedural discussion is insightful, but primarily narrative. It does not show domain denominators or whether deficiencies differ materially among domains.

**Required revisions:**

- Add a domain-by-evidence table or figure showing study counts, capability mix, rollout evidence, external validation, calibration, causal evidence, and safety.
- Distinguish general evidence requirements from domain-specific hazards and measurement limitations.
- Explain how the findings alter evaluation practice for biomedical informatics researchers rather than only world-model developers.

### M-5: Differentiation from prior reviews remains promising rather than fully demonstrated

**Anchor:** Introduction paragraph 4; Results §3.7; `existing-review-comparison.md`.

The operational audit is plausibly novel. However, "larger corpus" is not sufficient differentiation because the larger count may arise from broader eligibility. The manuscript does not reconcile which studies overlap with Chen et al., which are newly published, and which are included solely because of different boundaries.

**Required revisions:**

- Provide a study-level overlap analysis with the closest review.
- Explain every major eligibility difference.
- Identify conclusions that become possible only through MedWM-Eval.
- Avoid implying that capability ladders, causal cautions, or uncertainty requirements are novel.

### M-6: The original benchmark results should not remain in this review in their current form

**Anchor:** §5 Benchmark Implications.

The benchmark-design argument belongs in the review. The PhysioNet dataset choice and baseline results do not. They introduce original empirical findings without benchmark methods, split definitions, statistical procedures, or a formal results table in the manuscript.

Given the planned separate original paper, the review should retain only review-derived benchmark requirements and dataset task cards. The actual baseline experiment and model-ranking question should move to the original research paper.

**Required revisions:**

- Retitle the section as a review-derived benchmark or research agenda.
- Retain permissible-claim rules and dataset-selection requirements.
- Remove baseline performance findings and model-ranking language.
- Reserve the PhysioNet experiment, methods, splits, uncertainty analysis, and results for the original research paper.

### M-7: Reference and supplementary-artifact integrity needs substantial cleanup

**Anchor:** References; Data, Code, and Materials Availability.

Ten empirical references appear in the bibliography but are not cited in the manuscript: 4, 6, 8, 11, 18, 19, 24, 25, 32, and 43.

Several peer-reviewed versions are still represented as generic preprints or incomplete publication records, including references 46–48 and 50. Other entries contain placeholders such as "conference-paper" or inconsistent venue punctuation.

The visible `study-extraction-audit.md` still reports the superseded 55-study corpus, whereas the final corpus contains 50. Submission supplements must not mix current and obsolete artifacts.

**Required revisions:**

- Reconcile every citation against the final corpus.
- Cite every listed reference or remove it.
- Use the most authoritative publication version.
- Archive or clearly mark obsolete artifacts.
- Generate the supplement exclusively from the canonical 50-study final corpus.
- Run a final bidirectional citation and record-count audit.

## 6. Source and Figure Checks

### Source and corpus checks

- The main manuscript's headline counts match the corrected final-corpus MedWM-Eval summary.
- The final corpus contains 50 empirical studies and three reviews.
- The final corpus reports 19 planning, 15 action-conditioned, nine counterfactual, and seven passive-forecasting studies.
- Free-running rollout, horizon-resolved results, formal calibration, external validation, safety, public-code, and closed-loop counts in the manuscript are consistent with the final summary.
- A stale extraction audit still reports 55 empirical studies and must not be submitted as a current artifact.
- The review-comparison artifact correctly identifies the operational audit as the defensible novelty boundary, but also states that novelty depends on completing human verification.

### Figure 1

Figure 1 is visually clear but incomplete as a final review flow:

- Citation-chasing records are not shown as a separate route.
- Full-text exclusion reasons and counts are absent.
- The 5,335-record automated filter needs a validation note, not only a label.
- "Human verification pending" confirms that this is a developmental rather than submission figure.

**Required revision:** Rebuild the flow after the final human search and screening process, showing citation routes and exclusion-reason counts.

### Figure 2

Figure 2 is useful and readable, but it is a selected summary rather than a full evidence map:

- The rationale for selecting six evidence features is not provided.
- Unclear evidence is hidden from the bars.
- Denominators differ conceptually across causal evidence, external validation, and public-code confirmation.
- A capability-by-evidence heat map would support the central argument more directly.

**Required revision:** State selection rules, show unresolved evidence, label denominators consistently, and consider replacing or supplementing the figure with a capability-by-evidence matrix.

### Tables

All four manuscript tables require numbers, descriptive titles, and explicit callouts. The existing-review table should report inclusion-boundary differences, not only corpus size. The capability-evidence matrix is valuable and should be promoted as the central methodological table.

## 7. Minor Issues

### MI-1: The main conclusion is broader than the operationalized evidence

"Medical world models are advancing faster than their evaluation" is rhetorically effective but not directly operationalized.

**Revision:** Use a more evidence-specific conclusion tied to the observed frequencies.

### MI-2: "Frequently support claims" should be quantified

The abstract states that generative fidelity and retrospective agreement frequently support stronger claims, but it does not define "frequently."

**Revision:** Quantify the relevant studies or use wording tied directly to the coded evidence.

### MI-3: Causal-level terminology should remain rubric-bound

"Strong causal evidence" can be interpreted as a universal causal-quality judgement.

**Revision:** Consistently use "the strongest MedWM-Eval causal-evidence level."

### MI-4: The graphical abstract is absent

The provisional venue plan identifies a graphical abstract as a required submission asset.

**Revision:** Add it or explicitly mark it as pending outside the manuscript.

### MI-5: Planning terminology is inconsistent

The manuscript alternates among planning, closed-loop planning, offline decision evaluation, and simulation closed loop.

**Revision:** Define these once and use them consistently.

### MI-6: Version drift needs a management plan

Most included evidence appeared in 2026, and many sources are preprints.

**Revision:** Explain the final update date and how superseded preprints or peer-reviewed versions will be reconciled before submission.

## 8. Criterion-Bound Judgements

Scores are advisory, use a 1–5 scale, and are not venue-calibrated.

| Criterion | Score | Judgement and repair condition |
| --- | ---: | --- |
| Biomedical-informatics significance | 4 | Strong problem and broad relevance; retain the informatics focus rather than becoming a robotics catalogue. |
| Conceptual definition | 2 | Corpus boundary is insufficiently discriminative; requires strict criteria and sensitivity analyses. |
| Search and literature coverage | 2 | Missing databases and unvalidated automated filtering prevent a final evidence claim. |
| Review-method soundness | 2 | Human screening and extraction verification remain incomplete. |
| Differentiation from prior reviews | 3 | Operational audit is promising; requires study-level overlap and validated codebook evidence. |
| Claim framing | 3 | Generally careful, but capability assignment and several abstract claims require tightening. |
| Domain-specific synthesis | 3 | Insightful narrative, but insufficient domain-stratified evidence. |
| Figures and tables | 3 | Clear visuals; incomplete review flow, denominators, captions, and central evidence matrix. |
| Reference and source quality | 2 | Uncited entries, inconsistent publication versions, and stale supplementary artifacts. |
| Benchmark-section fit | 2 | Review-derived agenda fits; original baseline results should move to the separate research paper. |
| Clarity and organization | 4 | Clear, professional, and logically ordered overall. |

## 9. Questions for the Authors

1. What exact rule distinguishes a study's central empirical capability claim from aspirational or future-work language?
2. How do the principal counts change under a strict clinical, peer-reviewed, and explicitly self-identified world-model corpus?
3. Will all screening and evidence coding be independently verified by human clinical and methodological reviewers before submission?
4. Is §5 intended as a review implication or an original empirical contribution, and why should its baseline results remain in this article?

## 10. Decision-Changing Revision Priorities

1. Complete the human review workflow and rerun missing databases.
2. Validate the automated filter and stabilize the world-model definition.
3. Recalculate all results under source-quality and scope sensitivity analyses.
4. Strengthen domain-stratified synthesis and comparison with prior reviews.
5. Remove original baseline results from the review.
6. Rebuild the final figures, references, and supplement from one canonical 50-study corpus.

## 11. Final Recommendation

**Reject and resubmit after completing the review methodology.**

The manuscript has a publishable core, but its current evidence base is explicitly provisional. A fully human-verified revision that resolves search completeness, corpus boundaries, source-quality sensitivity, domain-specific synthesis, benchmark-section scope, and artifact integrity could become a strong Journal of Biomedical Informatics methodological review.
