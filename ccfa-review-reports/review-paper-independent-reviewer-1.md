# Independent Reviewer 1 Report

**Manuscript:** *Capability-Matched Evaluation of Medical World Models: A Scoping Review of Rollout, Causal Validity, and Safety*  
**Recommendation:** Major revision; not ready for journal submission  
**Review confidence:** High for the methodological and package-readiness assessment; moderate for source-level correctness because I did not independently re-screen all 6,692 records or re-extract all 85 empirical studies.

## Overall assessment

This is a timely and potentially valuable methodological review. Its strongest contribution is the separation of forecasting, action-conditioned simulation, counterfactual comparison, and planning claims, followed by an audit of the evidence reported for each interpretation. The manuscript is generally careful about denominators, distinguishes reporting prevalence from validity, avoids an unjustified aggregate quality score, and labels MedWM-Eval as preliminary. The correction history, publication-lineage work, candidate-level extraction, sensitivity analyses, and AI-use disclosure are unusually transparent.

The headline counts are internally consistent with the frozen corpus and analysis artifacts. I found direct artifact support for the 82-study primary corpus, the capability counts, the reported evidence frequencies, and the claim that no coded study combined free-running rollout, horizon-resolved results, formal calibration, and frozen external validation. The package validator also passes its technical checks. These facts establish internal traceability, but not yet independent validity.

Several acknowledged limitations remain genuine submission blockers. In particular, the study-selection and evidence-coding decisions have not been verified by qualified human reviewers; important engineering and citation databases have not been searched directly; eligibility criteria were refined during the same-day review workflow; and the principal framework has not undergone expert content validation. The manuscript should not be submitted as a completed scoping review until these issues are resolved.

## Major concerns

### 1. The corpus and material evidence codes lack qualified human verification

All screening, full-text assessment, extraction, capability classification, and MedWM-Eval coding were performed through separate AI-assisted contexts. The manuscript correctly states that this is not human inter-rater reliability. This distinction is consequential: 214 study-field disagreements required adjudication across 71 of 85 empirical studies, action-evidence agreement was the weakest coded domain, and the claim-provenance audit assigns 46 studies high priority for human review. The exact AI model builds, prompts, sampling settings, and runtime versions were also not preserved.

Before submission, qualified reviewers should verify at minimum every included publication, every full-text exclusion, the functional-equivalence boundary, all fields contributing to manuscript counts, and every record entering the joint-evidence intersections. Material disagreements should be independently adjudicated and the manuscript, tables, figures, and reliability results regenerated. A prespecified human audit of title/abstract exclusions is also needed to estimate residual selection error. Until this is completed, the principal prevalence and “0/82” findings remain provisional. This concern blocks submission.

### 2. Search coverage is not yet adequate for a journal scoping review of this engineering-heavy topic

The public search is broad but materially constrained. IEEE Xplore, the ACM Digital Library, Scopus, and Web of Science were not directly searched. OpenAlex and Crossref queries were capped or ranking-limited; the alternate OpenAlex search failed; arXiv required a limited HTML fallback; and citation chasing assessed only six records. These limitations are especially important because much of the target literature appears in engineering conferences, proceedings, repositories, and rapidly changing preprints.

The authors should complete authenticated searches in the missing engineering and citation databases, have the complete strategy reviewed by an information specialist, archive exact final queries and exports, repeat deduplication and lineage resolution, and update all downstream analyses. Search dates and publication status should then be refrozen. The present transparency is commendable, but disclosure does not substitute for adequate coverage. This concern blocks submission.

### 3. The protocol and functional eligibility boundary were developed retrospectively

The protocol, search correction, eligibility clarification, corpus freeze, extraction, and synthesis are all dated 12 September 2026. The functional-identity rule was operationalized after the initial phrase/domain filter was shown to miss eligible records and after a provisional corpus had been developed. Subsequent quality-control stages removed substantial numbers of proposed inclusions at the conceptual-equivalence boundary, and six records were re-adjudicated after extraction.

These corrections were sensible and are documented, but the manuscript wording that the protocol was “finalized” on that date may be read as implying a more prospective process than occurred. The final paper should explicitly characterize the protocol as retrospectively finalized, provide a versioned chronology showing which criteria changed before and after access to study-level results, and distinguish protocol amendments from error correction. Human reviewers should independently apply the final functional-identity rule. The explicit-world-model sensitivity analysis is useful, but a multi-definition sensitivity analysis should also show how the principal conclusions change under narrower and broader functional boundaries. This concern blocks submission until the final corpus boundary is independently confirmed.

### 4. MedWM-Eval and the “highest capability” hierarchy need content validation and softer claims

MedWM-Eval is a promising audit framework, but it is not yet a validated instrument. The highest-capability category can be triggered by language anywhere in the title, abstract, introduction, results, or conclusion, including potentially aspirational language. The fixed order of planning, counterfactual comparison, action-conditioned simulation, and forecasting is useful for display but does not make these capabilities universally ordinal; for example, procedural planning and clinical counterfactual estimation invoke different evidentiary dimensions.

The authors should:

- distinguish central empirically evaluated claims from aspirational or future-work claims;
- provide a multi-label capability analysis alongside the single display category;
- test sensitivity when claims are restricted to the abstract/results or explicitly demonstrated tasks;
- obtain content review from clinical, causal-inference, control, measurement, and safety experts; and
- report item-level human reliability after revising the codebook.

The graphical abstract currently calls the framework elements “Minimum evaluation evidence” and presents a “Supported interpretation.” That language is stronger than the manuscript’s appropriate description of a preliminary framework. It should instead use terms such as “proposed evidence considerations” and “interpretation supported when assumptions are met.” Because MedWM-Eval is the manuscript’s main methodological contribution, this concern blocks submission in the current form.

### 5. The reproducibility package is technically rich but not yet a submission-ready archive

The local artifacts provide good traceability, and the numerical validation succeeds. However, the durable computational provenance of the AI-assisted passes is incomplete, and the manuscript refers generally to materials that “accompany” the paper without a stable repository, version identifier, or DOI. The current formal supplement contains the correction history, while the complete queries, screening ledgers, full-text exclusion reasons, codebook, extraction matrix, adjudications, and claim-provenance records remain distributed across project directories.

Before submission, the authors should create a versioned, immutable archive containing the final protocol and amendments, complete search strategies and exports, deduplication/lineage ledger, included and excluded records with reasons, codebook, human verification files, final extraction and adjudication tables, analysis scripts, environment manifest, checksums, and figure source data. The Data, Code, and Materials Availability section should identify that archive precisely. This is a publication-readiness blocker.

## Minor comments

1. Figure 1 mixes raw initial retrieval counts with already deduplicated fresh alternate-search records. A standard PRISMA flow should show per-source identification counts, duplicate removal, automated exclusions, and summarized full-text exclusion reasons using comparable units.
2. Figure 2 places “strongest causal-evidence level” beside “formal calibration” and “frozen external validation,” while Table 1 reports the distinct explicit-estimand count. Make the distinction between an individual feature and the composite ordinal level visually unmistakable.
3. Report the distribution of full-text exclusion reasons in a readable supplementary table, not only in machine-readable records.
4. Preserve the “reported evidence” wording in the abstract and conclusion. Avoid converting absence of reporting into proof that an evaluation was not performed.
5. Clarify how peer-reviewed status was determined and recheck every preprint-to-publication lineage immediately before submission.
6. Define `NI`, `unclear`, and `no` beside the first table or figure where they affect denominators.
7. The benchmark agenda is appropriately framed as an author prioritization. Retain that boundary and avoid describing the selected ICU task as the uniquely established research priority.
8. Complete the author, affiliation, funding, competing-interest, CRediT, healthcare-professional involvement, and repository fields before submission.

## Verdict on submission blockers

**Yes, major concerns block submission.** The manuscript should not be submitted until the human verification, authenticated search update, independent eligibility confirmation, expert validation of MedWM-Eval, and stable reproducibility archive are complete. These issues are substantial but remediable. If they are resolved and the regenerated findings remain stable, the paper would be a credible and potentially useful methodological review for a biomedical informatics audience.
