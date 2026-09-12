# Independent Reviewer 2 Report

**Manuscript:** *Capability-Matched Evaluation of Medical World Models: A Scoping Review of Rollout, Causal Validity, and Safety*  
**Target journal:** *Journal of Biomedical Informatics*  
**Article type:** Scoping review with methodological framework  
**Review date:** 12 September 2026  
**Reviewer lens:** Medical-informatics editor and clinical domain reader  
**Recommendation:** Major revision before submission  
**Confidence:** High for manuscript-level and artifact-level findings; moderate for field-wide novelty because this review did not independently recode all 85 empirical studies or repeat the full systematic search

## 1. Scope and materials inspected

I reviewed the complete manuscript and the principal artifacts needed to assess its methods and claims:

- `manuscript/review.md`;
- the venue plan and technical validation report;
- the PRISMA-ScR/PRISMA-S reporting audit;
- the review protocol and protocol-deviation history;
- the MedWM-Eval codebook and pilot rubric;
- coding provenance and reliability reports;
- the claim-provenance audit and methodological appraisal;
- the existing-review comparison and the Chen et al. overlap analysis; and
- Figures 1–3 and the graphical abstract in their rendered forms.

I did not independently inspect every primary publication or reproduce every study-level coding decision. Therefore, this report assesses the manuscript's scientific argument, internal consistency, documented methods, and readiness for journal review. It does not certify the underlying extraction as correct.

## 2. Overall assessment

This is a timely and potentially useful methodological review. Its strongest contribution is not a new definition of a medical world model, but the attempt to connect the capability claimed by a model to the evidence required to interpret that claim. The distinction between prediction, action responsiveness, causal intervention comparison, and sequential planning is clinically important. The manuscript also handles several boundaries responsibly: it distinguishes action dependence from causality, simulation return from real-system safety, and a reporting prevalence estimate from a universal quality score.

The current version is nevertheless not ready for submission. Two central results remain methodologically exposed. First, all screening, extraction, and MedWM-Eval coding that supports the quantitative synthesis remains AI-assisted and lacks the qualified human verification that the manuscript itself identifies as necessary. Second, the headline four-way gap—no study combining free-running rollout, horizon-resolved results, calibration, and frozen external validation—uses all 82 primary studies as its denominator even though calibration and external validation are not equally applicable to every included system. This makes the zero intersection descriptively true as a corpus-wide reporting count, but not yet a capability-matched estimate of unmet evaluation requirements.

The paper also needs a firmer novelty boundary. A 2026 clinical digital-twin perspective by Vallée, which the search located but excluded from the review corpus, independently proposes a clinical-claim-to-evidence validation framework covering calibration, transportability, causal validity, utility, and monitoring. It need not be included in the counted review corpus if it fails the stated eligibility rule, but it is too close conceptually to omit from the manuscript's positioning.

My recommendation is **major revision**, with the quantitative synthesis and framework retained as the foundation. I would not recommend submission until the explicit blockers in Section 12 are resolved.

## 3. Principal strengths

### S1. The central distinction is clinically meaningful

Sections 1 and 4 clearly explain why evidence sufficient for one-step forecasting is insufficient for repeated rollout, why treatment conditioning is not causal identification, and why policy performance in a learned simulator does not establish safety under model mismatch. These distinctions are directly relevant to medical-informatics readers evaluating increasingly ambitious model claims.

### S2. The authors avoid a misleading aggregate quality score

The manuscript preserves separate evidence domains and changing applicability rather than summing them into a universal ranking. This is appropriate for a corpus spanning longitudinal records, imaging, biological systems, and embodied control.

### S3. The development history is unusually transparent

The initial discovery-filter failure, alternate-term search, exhaustive rescreen, post-extraction eligibility corrections, and remaining limitations are disclosed rather than hidden. The lineage ledger, disagreement files, source anchors, and generated summaries create a strong audit trail.

### S4. The causal boundary is generally well stated

Sections 3.3, 4.2, and 4.3 correctly separate action sensitivity from the identification of an unobserved treatment effect. The manuscript also names eligibility, time zero, treatment strategies, confounding, censoring, and positivity rather than using “causal” as a generic synonym for action-conditioned prediction.

### S5. The presentation is coherent and technically polished

The structured abstract, main text, five tables, three figures, and graphical abstract form a readable package. The current project validation indicates compliance with the planned journal word and display-item budgets. Figures 1–3 are visually clean, consistent, and legible in their vector/raster renderings.

## 4. Prioritized major concerns

### M1. Critical: the quantitative evidence map has not received qualified human verification

**Location:** Methods Sections 2.3–2.4; Limitations; coding-provenance and claim-provenance artifacts.

The manuscript reports two separate AI-assisted screening and coding passes, followed by source-grounded adjudication. It appropriately states that the resulting agreement statistics do not establish human inter-rater reliability or construct validity. The supporting provenance record further states that exact model build identifiers, prompts, sampling parameters, and runtime versions were not preserved for the original coding passes. The claim-provenance audit routes 46 of 85 empirical records to high-priority human review and only two to routine review.

This is not merely a disclosure issue. The paper's main numerical conclusions depend on judgments about the highest claim, free-running evaluation, calibration, external validation, causal estimands, and safety hazards. Agreement between two AI-assisted contexts shows process repeatability under that workflow, but does not establish clinically or methodologically correct coding.

**Why it matters:** Without qualified human verification, readers cannot know whether the headline counts reflect the source literature or a reproducible shared error in the AI-assisted rubric application. This affects every quantitative conclusion and would be a likely editorial objection for a clinical-methodology review.

**Required resolution:** Two qualified human reviewers should verify, with preserved disagreements and adjudication, all included studies, all full-text exclusions affecting the corpus boundary, and every field that contributes to a headline result. At minimum, this must cover capability classification, the four joint-gap features, causal applicability and estimands, external validation, and safety. The final manuscript should report the human process and regenerated counts. If title/abstract exclusions are handled through a validated sampling or prioritization design rather than full dual human rescreening, that design and its residual error risk must be explicit.

**Decision condition:** This is a submission blocker. My methodological-soundness assessment would improve only after the reported synthesis is regenerated from verified decisions.

### M2. Critical: the central 0/82 joint gap is not analyzed on a capability-matched applicability denominator

**Location:** Abstract Results and Conclusion; Sections 3.4, 5, and 6; Table 1; Figure 2.

The manuscript repeatedly highlights that no study combined free-running rollout, horizon-resolved results, formal calibration, and frozen external validation. The count is internally reproducible. However, the denominator is the entire 82-study primary corpus. The manuscript simultaneously acknowledges that calibration is a reporting prevalence rather than a compliance rate because deterministic systems may not expose a predictive distribution. Table 3 also makes external validation conditional on transport or deployment claims rather than universally mandatory.

The problem becomes more consequential when this corpus-wide intersection is described as the “strongest numerical result” and used to select the first benchmark opportunity. Procedural deterministic controllers, image-generation systems, biological simulators without transport claims, and probabilistic patient forecasters do not share one four-item applicability set. A zero across all 82 studies therefore demonstrates that no publication reported all four labels; it does not establish that 82 studies failed a matched standard or that this is the most prevalent capability-specific deficit.

**Why it matters:** The review's stated innovation is capability-matched evaluation. Its most prominent statistic currently departs from that principle. The denominator choice can exaggerate the apparent universality and priority of the selected gap.

**Required resolution:** Define a prespecified applicability denominator for each component and intersection. For example, identify studies that make multistep probabilistic forecasting claims and for which a frozen external or temporal transport assessment is relevant. Report:

1. total-corpus reporting prevalence;
2. applicable-study prevalence;
3. known-study prevalence after unclear records are removed; and
4. the exact study-level intersection within the applicable subset.

If applicability cannot be determined reliably, retain the 0/82 value only as a descriptive corpus-wide intersection and remove language implying that it is the strongest or most persistent unmet requirement. The benchmark may still be proposed as an author-prioritized, feasible response, but not as a uniquely demonstrated consequence of the current denominator.

**Decision condition:** This is a submission blocker because it affects the abstract, conclusion, Figure 2, benchmark agenda, and the paper's central claim.

### M3. Major: the “highest capability claimed” taxonomy is vulnerable to rhetorical and label-based classification

**Location:** Eligibility Section 2.1; MedWM-Eval coding Section 2.4; Results Sections 3.1 and 3.3; Table 3.

The framework assigns one display category according to the highest claim found anywhere in the title, abstract, introduction, results, or conclusion, using a fixed hierarchy of planning, counterfactual comparison, action-conditioned simulation, and passive forecasting. This is simple and auditable, but it can classify a study by its strongest rhetorical sentence rather than its primary evaluated use. It also compresses clinically different systems into one ordinal ladder. Treatment planning from observational EHR data, surgical robot control, simulated neural stimulation, and constrained infectious-disease policy optimization all become “planning,” although their causal, safety, and external-validity requirements differ.

The corpus boundary has a related asymmetry. A conventional disease-progression or trial-simulation model is excluded unless authors give it a qualifying simulator/twin identity or use it as an internal planning environment. Thus, two technically similar dynamic models may receive different eligibility decisions because of author terminology or stated identity.

**Why it matters:** A medical-informatics reader needs to know whether the review maps computational capability, clinical claim semantics, author rhetoric, or field self-identification. These are not interchangeable constructs.

**Required resolution:** Preserve the four categories as a useful display, but add a second, nonordinal axis that separates:

- predictive versus causal versus control interpretation;
- observational clinical action versus commanded procedural action;
- primary evaluated capability versus aspirational or discussion-level claim; and
- explicit world-model identity versus functionally equivalent simulator identity.

Provide sensitivity analyses using the primary evaluated claim and the explicit-world-model subset, and show how often the highest-claim rule changes classification relative to the primary experimental evidence. Include several adjudicated boundary examples in the Supplement.

**Decision condition:** The taxonomy can remain, but the manuscript should no longer present the four classes as a single unqualified clinical capability ladder.

### M4. Major: the novelty boundary omits a directly overlapping claim-based validation framework

**Location:** Introduction; Section 3.6; Table 2; Discussion.

The search artifacts show that the review located but excluded Vallée's 2026 perspective, *From digital twins to clinically trustworthy twins: a clinical-claim-based validation framework for personalized digital health* (DOI: 10.3389/fdgth.2026.1908794). That article explicitly links evidentiary burden to clinical claim rather than architecture and discusses calibration, uncertainty, transportability, causal validity, real-world utility, fairness, target-trial emulation, and monitoring. These concepts substantially overlap the motivation and high-level structure of MedWM-Eval.

Exclusion from the counted review corpus may be defensible because the article is a perspective rather than a substantial empirical synthesis. Exclusion from the manuscript's intellectual positioning is not. Table 2 currently makes the present review appear more distinct from prior claim-matched validation work than the available literature supports.

**Why it matters:** Reviewers may interpret the framework as a repackaging of a contemporaneous digital-twin validation argument unless the difference is made explicit.

**Required resolution:** Cite and discuss this perspective as adjacent methodological work. State that the conceptual principle—matching evidence to clinical claim—is shared. Then locate novelty in the publication-lineage-resolved empirical audit, operational coding rules, study-level source anchors, applicability tracking, and observed intersections. The manuscript should avoid implying that MedWM-Eval introduces the claim-to-evidence idea itself.

**Decision condition:** The novelty claim remains defensible if it is narrowed to the empirical implementation and audit rather than the conceptual hierarchy.

### M5. Major: the framework's clinical and safety validity is not yet established, and the graphical abstract overstates its status

**Location:** Sections 4.1–4.5; Table 3; graphical abstract; Limitations.

The text describes MedWM-Eval as preliminary and Table 3 generally uses “recommended,” “needed,” or “scope dependent.” The graphical abstract instead uses “claims require” and “minimum evaluation evidence.” This converts a proposed, unvalidated framework into an apparent consensus standard.

The graphical abstract also lists the evidence for closed-loop planning as decision utility, mismatch stress tests, safety, and external validation. For treatment-planning systems, the manuscript's own Table 3 requires a causal estimand and assumptions. Omitting that element from the most visible summary weakens the causal boundary the paper otherwise handles carefully.

The rubric's safety level 2 is also broad: a study can qualify through defined hazards with severity, stress tests, constraints, recovery/override, **or** subgroup worst cases. These are not equivalent demonstrations, and the appropriate safety case differs fundamentally between a clinical treatment recommender, a surgical robot, and a biological simulator.

**Why it matters:** Readers may use the framework as a checklist or certification instrument despite the manuscript's caveat. In medicine, overstating a preliminary safety and causal framework is itself a responsible-research concern.

**Required resolution:** Obtain documented review by healthcare professionals and relevant specialists in causal inference, clinical prediction, control/robotics, and safety. Report how their feedback changed the framework. Revise the graphical abstract to use “proposed evidence considerations” or equivalent language, and explicitly include causal identification for treatment-planning claims. Decompose safety evidence into domain-specific minimum elements or state clearly that the current safety domain maps reporting breadth rather than sufficiency.

**Decision condition:** Expert content validation and healthcare-professional involvement are submission blockers for this journal and for the scientific credibility of the framework.

### M6. Major: search completeness is not yet adequate for a field with substantial engineering and proceedings literature

**Location:** Methods Section 2.2; Limitations; protocol and PRISMA-S audit.

The search did not directly query IEEE Xplore, ACM Digital Library, Scopus, or Web of Science. This limitation is especially material here: 24 primary studies are procedural/embodied, several included studies are from IEEE, ACM, CVPR, ICCV, MICCAI, KDD, EMBC, and robotics venues, and only 33 of 82 primary records are classified as peer reviewed. OpenAlex, Crossref, and citation chasing provide partial coverage but are not equivalent to an authenticated update of the principal engineering and citation databases.

The protocol, search correction, conceptual-equivalence rule, and corpus freeze also occurred in the same dated work cycle. The transparency is commendable, but prospective protection from post hoc boundary choices is limited.

**Why it matters:** An editor may reasonably question both recall and stability of the corpus, particularly where the claimed novelty depends on no study satisfying a four-way intersection.

**Required resolution:** Complete the authenticated IEEE/ACM and Scopus or Web of Science update; have the final strategy peer reviewed by an information specialist; archive the exact exports and deduplication logic; and rerun all counts after incorporating eligible records. Preserve the existing development history and clearly label the final preregistered or time-stamped analysis freeze.

**Decision condition:** This is a submission blocker. A final update is necessary even if it does not materially change the conclusions.

## 5. Minor and presentation comments

1. **Definition in the Introduction:** Add one concise operational definition that distinguishes the review's “medical world model” from ordinary longitudinal prediction, disease-progression modeling, digital shadows, and conventional simulation. The current definition is distributed across Sections 1 and 2.

2. **Abstract headroom:** The validated abstract is 337 words against a 350-word target. The required denominator and human-verification revisions will likely add text. Shorten now rather than risk an over-limit final abstract.

3. **PRISMA flow:** Figure 1 reports 325 full-text exclusions without reason categories. Include the principal exclusion-reason counts in the figure or a clearly signposted supplementary table.

4. **Table 1 denominators:** Use a consistent `n/N (%)` format and separate total-corpus, applicable, known, and unclear counts. The calibration row currently combines 5/82 and 5/37 in prose, which invites denominator confusion.

5. **Terminology consistency:** Replace “strongest causal-evidence level” in Figure 2 with the manuscript's defined term, such as “directly auditable causal evidence,” if that is the intended numerator.

6. **Figure 3 applicability:** Cells such as causal evidence `0/1` for action-conditioned models are visually comparable to `0/18` for counterfactual models despite radically different denominators. Use hatching, an applicability marker, or a separate panel to prevent percentage-color comparisons across tiny denominators.

7. **Graphical abstract:** Replace “Minimum evaluation evidence” with “Proposed capability-matched evidence” and “claims require” with wording that reflects the preliminary status.

8. **Benchmark agenda:** Section 5 is useful but reads partly as a bridge to the authors' next empirical paper. Keep the review's contribution primary. Present the ICU benchmark as one worked example and give the selection rule enough detail that another team could choose a different domain from the same evidence map.

9. **Peer-review status:** Define how conference proceedings, journal articles, preprints, repositories, and accepted-but-unverified records were assigned to the 33-study peer-reviewed subset. Repeat this definition in the Supplement.

10. **Safety wording:** Avoid treating aggregate adverse-event reporting, a collision count, a rule-based override, and a prespecified stress test as points on one simple continuum unless the rubric explains what each supports.

11. **External validation:** Distinguish institutional, temporal, geographic, device, and simulated-to-real validation in the main results. A single binary flag obscures clinically important differences in transport.

12. **Observation process:** The discussion correctly notes missingness and measurement timing, but this evidence is not given the same visibility as calibration and external validation. Since it is central to EHR trajectory validity, consider reporting it in Table 1 or Figure 3.

13. **Statement of Significance:** Align the labels exactly with the final journal template, including “What This Paper Adds,” when the submission package is prepared.

14. **Declarations:** Replace the placeholder competing-interest, funding, and CRediT sections before submission. The generative-AI declaration is appropriately explicit, but the final wording should be checked against the journal's current required language.

15. **Prose:** The manuscript is generally readable. The densest passages are Sections 2.2–2.5 and 3.5, where multiple denominators and sensitivity strata are introduced in long sequences. A small denominator glossary or compact supplementary table would reduce cognitive load.

## 6. Tables and figures

The visual package is professionally designed and materially improves the paper. Figure 2 is the clearest summary of the evidence landscape, and Figure 3 usefully exposes domain differences. The main visual objections are interpretive rather than aesthetic:

- Figure 2 makes the all-study denominator visually dominant even where applicability differs.
- Figure 3's color encoding can imply comparability across cells with very different applicable denominators.
- The graphical abstract presents preliminary recommendations as minimum requirements and omits causal identification from treatment-planning evidence.
- Figure 1 should display or more directly route readers to full-text exclusion reasons.

These changes should be made before submission because many readers will rely on the figures without reconstructing the denominator rules from the Methods.

## 7. Novelty and journal fit

The topic fits *Journal of Biomedical Informatics*: the contribution is methodological, cross-domain, and concerned with how dynamic biomedical AI systems should be evaluated and interpreted. The paper also goes beyond an architecture survey by supplying a study-level evidence map.

The novelty is meaningful but narrower than the manuscript presently suggests. Recent reviews already provide capability ladders, translational concerns, simulator-validity discussions, and causal/safety caveats. Vallée's 2026 digital-twin perspective additionally supplies a close claim-to-evidence framework. The defensible novelty is therefore:

1. operationalizing evidence domains at study level;
2. applying them to a larger lineage-resolved empirical corpus;
3. preserving applicability and source anchors;
4. quantifying reported evidence and intersections; and
5. deriving domain-specific evaluation questions from that audit.

This positioning is sufficient for a methodological review if the human verification and denominator problems are corrected. Without those corrections, the manuscript risks appearing simultaneously less novel conceptually and less secure empirically than its framing implies.

## 8. Claim-support audit

| Central claim | Current support | Judgment | Required change |
| --- | --- | --- | --- |
| Medical world-model claims span forecasting, action-conditioned simulation, counterfactual comparison, and planning | Operational rubric plus 82-study primary coding | Plausible and useful, but sensitive to highest-rhetorical-claim classification | Add primary-evaluated-claim and two-axis sensitivity analyses; resolve M3 |
| Reporting of calibration, causal identification, external validation, and explicit safety testing is limited | Study-level coded counts with source anchors | Descriptively supported, pending human verification | Complete human verification and regenerate counts; resolve M1 |
| No study combines free rollout, horizon reporting, calibration, and frozen external validation | Reproducible 0/82 corpus-wide intersection | Descriptively true for the coded corpus, but not yet an applicability-matched deficit estimate | Reanalyze on an applicable denominator and revise the claim; resolve M2 |
| MedWM-Eval provides capability-matched evidence considerations | Preliminary codebook and narrative framework | Conceptually coherent but not validated as a minimum standard | Obtain multidisciplinary content validation and revise status language; resolve M5 |
| The framework is differentiated from existing reviews | Comparison with eight included reviews | Partly supported; close excluded perspective is missing from positioning | Discuss Vallée 2026 and narrow novelty; resolve M4 |
| An ICU calibrated-rollout benchmark is directly motivated by the review | Author prioritization table plus four-way intersection | Reasonable as a worked example, not uniquely compelled by current evidence | Separate empirical gap from author prioritization and fix denominator; resolve M2 |

## 9. Reproducibility and auditability

The artifact package is a substantial strength. Search logs, screening decisions, exclusion reasons, lineage records, extraction files, coding passes, adjudications, scripts, and figure sources appear to be preserved. The technical validation report also checks counts, references, figures, and journal limits.

The main reproducibility limitation is not file availability but provenance and validation. The original AI coding runs cannot be exactly replayed because model and prompt metadata were not captured. More importantly, computational replay would still not establish clinical correctness. Human verification should become the canonical evidence layer, with the AI-assisted files retained as developmental provenance.

## 10. Editorial risk assessment

| Check | Status | Editorial interpretation |
| --- | --- | --- |
| Topic and article-type fit | Pass | Strong fit for a methodological biomedical-informatics review |
| Word, abstract, and display budget | Pass in current technical validation | Little headroom remains for required revisions |
| Reviewability and artifact traceability | Pass with concern | Strong audit trail, but underlying decisions are not human validated |
| Search completeness | Fail for submission readiness | Authenticated engineering/citation sources and information-specialist review are pending |
| Clinical expertise and framework validity | Fail for submission readiness | Healthcare-professional and multidisciplinary expert involvement are pending |
| Claim-evidence alignment | Major concern | Central four-way gap uses a non-matched denominator |
| Novelty positioning | Major concern | Close 2026 claim-based validation perspective is not discussed |
| Declarations and metadata | Incomplete | Competing interests, funding, CRediT, affiliations, and stable repository remain pending |

**Desk-rejection risk in the current state:** High.  
**Desk-rejection risk after the listed blockers are resolved:** Low to moderate, with the remaining decision likely to turn on novelty and the perceived value of the cross-domain synthesis.

## 11. Ratings

| Dimension | Score | Evidence and deduction | Condition for improvement |
| --- | ---: | --- | --- |
| Significance and journal relevance | 4/5 | Important and rapidly developing topic with clear medical-informatics relevance | Preserve the clinically bounded claim hierarchy |
| Conceptual contribution and novelty | 3/5 | Useful operational audit, but the claim-to-evidence concept overlaps prior reviews and Vallée 2026 | Narrow novelty to the empirical implementation and cite the closest framework |
| Taxonomy and construct validity | 3/5 | Highest-claim hierarchy is interpretable but sensitive to rhetoric, domain, and author labels | Add a two-axis taxonomy and sensitivity analyses |
| Review-method soundness | 2/5 | AI-assisted decisions and adjudications lack qualified human verification; search update is incomplete | Complete human verification and authenticated search update |
| Claim-evidence support | 3/5 | Most counts are traceable, but the headline joint-gap denominator is not capability matched | Reanalyze applicability and regenerate the abstract, figures, and conclusions |
| Clinical, causal, and safety boundaries | 3/5 | Causal distinctions are strong; framework content validity and safety sufficiency remain unvalidated | Obtain multidisciplinary expert review and revise graphical summary |
| Clarity and presentation | 4/5 | Coherent narrative and strong figures, with denominator density and graphical overstatement as local issues | Simplify denominator presentation and align all visuals with preliminary status |
| Reproducibility and auditability | 4/5 | Extensive artifacts and provenance are available | Establish verified human coding as canonical and archive final search exports |
| Submission readiness | 2/5 | Multiple acknowledged human, search, analytical, and metadata gates remain open | Resolve all blockers in Section 12 |

## 12. Explicit submission blockers

The manuscript should not be submitted until all of the following are complete:

1. **Qualified human verification:** Verify corpus eligibility, material exclusions, extraction fields, capability classifications, and every coding field supporting headline results; adjudicate and regenerate the synthesis.
2. **Applicability-matched reanalysis:** Recalculate the four-way gap and related intersections using explicit applicable and known denominators; revise the abstract, Figure 2, benchmark agenda, discussion, and conclusion.
3. **Authenticated search update:** Search IEEE Xplore, ACM Digital Library, and Scopus or Web of Science; complete information-specialist review; archive final queries, exports, and lineage decisions.
4. **Framework content validation:** Document substantive review by healthcare professionals and appropriate causal, prediction, control, and safety experts.
5. **Novelty correction:** Cite and compare the Vallée 2026 clinical-claim-based validation framework and narrow the novelty claim to the study-level empirical audit.
6. **Graphical-abstract correction:** Remove “minimum”/universal-requirement wording and restore the causal-identification requirement for clinical treatment planning.
7. **Submission metadata:** Supply author list and affiliations, funding and funder role, competing interests, CRediT roles, acknowledgments, corresponding-author details, and a stable repository/archive location.

## 13. Questions for the authors

1. How many studies remain in the four-way intersection denominator after requiring that all four evidence features be applicable to the model's stated use?
2. How often does classification by the highest claim anywhere in the paper differ from classification by the primary evaluated capability in the Results?
3. Which included studies entered primarily because the authors called them a world model, twin, or simulator, and which entered through the functionally equivalent planning criterion?
4. Will qualified humans verify all 1,785 study-field decisions, or will the authors use a prespecified risk-based verification design? What residual error will that design permit?
5. Why is Vallée 2026 excluded from the intellectual comparison despite proposing a directly overlapping clinical-claim-to-evidence framework?
6. What evidence should be mandatory, rather than optional or domain dependent, before a treatment-planning world model can support a clinical recommendation?
7. How will the framework distinguish safety reporting from evidence sufficient for a safety claim in clinical, biological, and embodied systems?

## 14. Revision priorities

| ID | Priority | Required action | Status |
| --- | --- | --- | --- |
| M1 | Critical | Complete qualified human verification and regenerate all affected counts | Open; submission blocker |
| M2 | Critical | Rebuild joint-gap analyses with capability-matched applicability denominators | Open; submission blocker |
| M6 | High | Complete authenticated database update and information-specialist review | Open; submission blocker |
| M3 | High | Add a two-axis taxonomy and primary-evaluated-claim sensitivity analysis | Open |
| M4 | High | Reposition novelty against Vallée 2026 and other closest frameworks | Open; submission blocker |
| M5 | High | Obtain expert content validation and revise framework/graphical-abstract claims | Open; submission blocker |
| P1 | Medium | Clarify denominators and applicability visually in Tables 1 and Figures 2–3 | Open |
| P2 | Medium | Add full-text exclusion-reason counts and publication-status definitions | Open |
| P3 | Required | Complete declarations, contributor metadata, and stable artifact archiving | Open; submission blocker |

### Final recommendation

**Major revision before submission.** The paper has a strong and relevant methodological core, a commendably transparent evidence package, and a potentially publishable empirical audit. The current version should not yet be presented as a completed scoping review because its quantitative conclusions remain AI-verified rather than expert-verified, its most prominent joint gap is not calculated on a matched applicability denominator, and its framework is positioned too strongly relative to both its preliminary validation status and close prior conceptual work.
