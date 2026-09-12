# Independent Reviewer 2 Follow-Up Report

**Manuscript:** *Beyond One-Step Error: Free-Running Evaluation of ICU Chart-Process World Models Across Cohorts*  
**Review date:** 12 September 2026  
**Review round:** Follow-up review after Reviewer 2 major revision  
**Target venue:** Not specified; assessed against a general medical-AI or clinical-informatics journal standard  
**Materials inspected:** Revised manuscript, prior Reviewer 2 report, supplementary results, protocol and amendment records, frozen five-seed results, variable-level result files, current validation report, and all regenerated figures with their alignment and collision audits  
**External literature search:** Not repeated for this follow-up; related-work judgment is limited to the supplied manuscript, companion review, and local reference materials  

## New recommendation

**Minor revision before submission.**

The revised manuscript has resolved the main scientific overclaiming that drove my previous major-revision recommendation. It now defines the modeled object as the recorded ICU chart process, removes calibration from the title, describes the spread analysis as finite-draw adaptation, bounds the constraint findings, reports effective support, adds original-unit variable results, and qualifies the scoping-review novelty statement. The central descriptive conclusion is supported: under this benchmark, one-step error, long-horizon error, finite-draw uncertainty behavior, mask prediction, and narrow chart-state constraints do not yield the same implementation ranking.

I do not consider a full five-seed 100-trajectory rerun essential for the manuscript's newly narrowed claims. The paper no longer represents the 20-draw analysis as a direct estimate of infinite-draw model calibration. However, the current submission package still contains terminology and metric inconsistencies that must be corrected. Most importantly, Figure 1 still says “Uncertainty calibration” and “Physiological validity,” Figure 3 still labels the adapted condition “spread-recalibrated,” and the main table continues to call deviation from 0.90 a “90% coverage error” immediately after explaining that the implemented 20-draw interval is not a finite-sample 90% interval.

## What is now scientifically convincing

1. **The chart-process claim boundary is clear.** The title, Abstract, Introduction, Methods, Discussion, and Conclusion now consistently distinguish recorded values, measurement masks, and carry-forward chart states from latent patient physiology. Treatment-independent patient simulation is no longer implied.

2. **The uncertainty result is appropriately narrowed in the prose.** Methods 2.7 explicitly states that the 20-draw quantiles, sample mean, CRPS, and Gaussian score contain Monte Carlo error. The manuscript correctly describes the 20/50/100 analysis as demonstrating dependence rather than convergence and limits the robust underdispersion conclusion primarily to the state-space model.

3. **Constraint language is substantially improved.** The manuscript now calls the checks “prespecified chart-state constraint diagnostics,” explains asynchronous carry-forward ages, discloses the absence of a matched observed-chart reference, and states that the rates are neither simultaneous-physiology estimates nor safety evidence.

4. **Aggregate-error interpretation is more clinically honest.** The new original-unit analysis shows that the Transformer/ridge difference is heterogeneous: the neural model is better for several vital signs while ridge is better for temperature, creatinine, glucose, and white-cell count. The paper explicitly states that no minimum clinically important difference was defined.

5. **Support and inferential scope are now transparent.** The revised text distinguishes common anchor eligibility from horizon-specific observed-target support and explains that patient-bootstrap intervals are conditional on the five fitted neural instances.

6. **Positioning has improved.** The Introduction now identifies the scoping review as AI-assisted and pending qualified human verification, and it adds adjacent work on irregular clinical dynamics, synthetic longitudinal records, and external validation. The novelty language is no longer framed as a settled field-wide first claim.

7. **The prose is professional and non-defensive.** The paper presents corrections and limitations directly without turning the Discussion into a rebuttal. Negative results remain visible.

## Status of the previous major concerns

| Prior ID | Status | Follow-up judgment |
| --- | --- | --- |
| R2-M1: trajectory-count dependence | Resolved for the narrowed claim | The title and conclusions no longer claim underlying model calibration. Finite-draw dependence is disclosed in the Abstract, Methods, Results, Figure 3 caption, Discussion, and limitations. A higher-draw full rerun would strengthen the paper but is no longer required for the bounded descriptive conclusion. |
| R2-M2: physiological-validity and safety overclaim | Partially resolved | The manuscript and Figure 4 are appropriately bounded. Figure 1 still contains “Physiological validity,” so the visual package has not fully adopted the revision. |
| R2-M3: chart process versus patient state | Resolved | The modeled object and omitted treatment, discharge, death, and latent physiology are stated clearly. |
| R2-M4: aggregate NMAE lacks clinical interpretation | Substantially resolved | Original-unit variable results and the absence of a clinically important threshold are now reported. Table S1 still needs units and complete submission packaging. |
| R2-M5: incomplete inferential scope | Resolved for descriptive reporting | The paper now explicitly distinguishes patient sampling from training-run uncertainty and labels non-NMAE uncertainty as across-seed descriptive variation. |
| R2-M6: preliminary novelty and thin positioning | Partially resolved | The preliminary-review caveat is appropriate and four adjacent references were added. The closest-work discussion remains short but no longer supports an overstrong novelty claim. |

## Remaining scientific and publication blockers

### R2-R1 — The regenerated figures retain claims that the manuscript deliberately removed

**Severity:** High but mechanically fixable  
**Origin:** Revision regression in the presentation package  
**Location:** Figure 1 panel c; Figure 3 legend

Figure 1 still labels measured evidence as “Uncertainty calibration” and “Physiological validity.” Figure 3 still uses “External spread-recalibrated.” These labels conflict with the revised manuscript's central distinction between finite-draw uncertainty, spread adaptation, and narrow chart-state constraint consistency.

This is not merely stylistic. Many readers will infer the contribution from the figures before reading the qualifications in Methods 2.7 or Results 3.5. The current figure language restores exactly the two broader claims that the revision correctly removed from the text.

**Required change:** Regenerate Figure 1 with labels such as “Finite-draw uncertainty” and “Chart-state constraint diagnostics.” Replace “spread-recalibrated” in Figure 3 with “spread-adapted.” Recheck all SVG, PDF, TIFF, and PNG exports and rerun the figure audits.

### R2-R2 — “Coverage error from nominal 90%” is inconsistent with the finite-draw interpretation

**Severity:** Moderate scientific issue  
**Origin:** Previously latent issue made explicit by the revised finite-sample analysis  
**Location:** Methods 2.7 and outcome 4 in 2.8; Results 3.3; Table 3.7; Figure 3

The revision explains that the linearly interpolated 5th–95th percentile interval from 20 draws has expected finite-sample coverage near 0.814 under the stated idealized calculation, rather than 0.90. The paper nevertheless retains “absolute error from nominal 90% interval coverage” as a primary outcome, labels Table 3.7 “12 h 90% coverage error,” and uses a 0.90 reference line in Figure 3.

The observed coverage values are valid descriptions of the implemented empirical interval. The problem is calling distance from 0.90 a calibration error when the finite-draw construction is not designed to attain 0.90. For GRU-D and the Transformer, this can make a finite-draw quantile property look like model underdispersion.

**Required change:** Rename the reported quantity as coverage of the empirical 5th–95th percentile interval and avoid interpreting distance from 0.90 as model calibration error. If a reference remains, label 0.90 as the infinite-draw target and add the finite-draw expected reference for the implemented quantile rule. The simplest repair is to report coverage directly in the main table and reserve “underdispersion” for conclusions supported by the trajectory-count sensitivity, as already done for the state-space model.

### R2-R3 — The new variable-level supplement is not yet submission-ready

**Severity:** Moderate presentation and reproducibility issue  
**Origin:** New revision artifact  
**Location:** Supplementary Table S1; Results 3.2; Limitations

The added analysis is valuable, but Table S1 lists variable abbreviations without their measurement units. It displays ten selected variables while directing readers to a local filesystem path for the complete 24-variable table. A submitted supplement cannot depend on `experiments/results/...` being available on the authors' machine.

The variable-level values also appear to be observed-target-weighted metrics, whereas the main NMAE is aggregated within patient and then across patients. That distinction should be stated so readers do not treat Table S1 as a direct additive decomposition of the patient-macro result.

Finally, the limitations section says, “Variable-level clinical-unit results were not developed,” which directly contradicts Results 3.2 and Supplementary Table S1. The intended limitation appears to be lack of clinician-validated importance thresholds, not absence of variable-level results.

**Required change:** Include the complete 24-variable table in the submitted supplement, add units and aggregation definitions, remove the local-path dependency, and correct the stale limitations sentence.

### R2-R4 — Reproducibility details remain thinner than the available implementation

**Severity:** Moderate  
**Origin:** Inherited, partially unresolved  
**Location:** Methods 2.6 and 2.10; supplement

The manuscript still omits several material training details that are available in the implementation: mask-loss weight, state-space KL weight, early-stopping patience, output-scale bounds, random patient-window sampling, exhaustive validation-window construction, and exact checkpoint selection. The local artifacts make the study auditable here, but journal readers should not need access to private workspace files to reconstruct the training protocol.

**Required change:** Add a compact supplementary implementation table covering the complete model and training configuration. This does not require new experiments.

### R2-R5 — Related-work positioning is improved but remains adjacent rather than closest

**Severity:** Moderate  
**Origin:** Inherited, partially resolved  
**Location:** Introduction paragraphs 3–4; References 9–12

The new paragraph is useful, but EHR-Safe and HALO are primarily synthetic-record generators, and the external-validation citation concerns deterioration prediction rather than free-running multivariate trajectory simulation. These are relevant adjacent works, not necessarily the closest empirical comparators.

Because the manuscript now presents the review-derived gap as preliminary, this is not a fatal novelty problem. Still, the final paper should identify at least a small number of the closest ICU or longitudinal clinical trajectory forecasters and state exactly which components they do or do not evaluate. The companion review can guide this selection after human verification.

**Required change:** Expand the related-work paragraph modestly with the closest task-level comparators. Avoid restoring a “first study” claim.

## Figure and supplement assessment

The regenerated figures pass the local alignment and collision audits and are visually legible. Figures 2 and 4 now have substantially better captions: uncertainty bars, seven-model ranking, chart-state scope, and non-severity heat-map color are all explained. Extended Data Figure 1 appropriately states that the sensitivity uses one trained seed, separate streams, and no repeated-stream Monte Carlo intervals.

The main remaining figure issue is semantic consistency, not graphical quality. Figure 1 and Figure 3 must be regenerated with the manuscript's revised terminology.

The supplement is useful but currently too short to serve as the complete reproducibility supplement promised by the manuscript. It should absorb the full variable table and implementation configuration rather than pointing to workspace paths.

## Claim-to-evidence judgment after revision

| Current claim | Follow-up judgment |
| --- | --- |
| One-step and long-horizon aggregate error can rank the tested implementations differently | Supported |
| GRU-D-style and Transformer are effectively tied at external 12 hours under the five fitted instances | Supported with the stated fixed-instance boundary |
| The state-space implementation is inaccurate and remains strongly underdispersed at 100 draws | Supported by the available one-seed sensitivity; appropriately not generalized to the architecture class |
| Spread adaptation changes the finite-draw empirical distribution without changing point forecasts or rollout states | Supported |
| GRU-D-style and Transformer are intrinsically miscalibrated | No longer claimed; appropriately unresolved |
| Aggregate NMAE improvements are clinically important | Not claimed; original-unit heterogeneity is now shown |
| Accuracy and narrow chart-state constraint rates provide different implementation rankings | Supported |
| The constraints establish physiological validity or clinical safety | Correctly rejected in the text, but still implied by Figure 1 |
| Cohort B is evidence of general deployment validity | Correctly rejected |
| The benchmark establishes causal, counterfactual, treatment, or policy validity | Correctly rejected |

## Frozen comparison contract

The comparison uses the seven dimensions and 1–5 anchors from the first Reviewer 2 report. Because the first report did not state weights, this follow-up applies the following fixed weights to both versions: contribution 15%, technical soundness 20%, evidence and clinical validity 20%, claim discipline 15%, clarity 10%, positioning 10%, and reproducibility 10%. A weighted increase of at least 0.25 is classified as improved. This was not a blinded comparison.

## Relative-progress scorecard

| Dimension | Historical | Current | Delta | Weight | Evidence |
| --- | ---: | ---: | ---: | ---: | --- |
| Contribution and significance | 4 | 4 | 0 | 15% | Same useful evaluation contribution |
| Technical soundness | 3 | 4 | +1 | 20% | Finite-draw estimand and limitations are now explicit; R2-R2 remains |
| Evidence and clinical validity | 3 | 4 | +1 | 20% | Chart-process boundary and original-unit heterogeneity added |
| Claim discipline and responsible research | 4 | 4 | 0 | 15% | Text improved substantially, but Figure 1 prevents a score increase |
| Clarity and organization | 4 | 4 | 0 | 10% | Better support and captions; stale limitation and figure terminology remain |
| Positioning and related work | 2 | 3 | +1 | 10% | Preliminary-review caveat and adjacent work added |
| Reproducibility and auditability | 4 | 4 | 0 | 10% | Strong artifacts; complete supplementary configuration and stable release remain pending |

**Historical weighted score:** 3.40/5  
**Current weighted score:** 3.90/5  
**Weighted delta:** +0.50  
**Relative-progress classification:** **Improved**

No dimension decreased. The new issues are presentation regressions or newly exposed consistency problems, not evidence that the underlying frozen results worsened.

## Absolute-readiness scorecard

| Dimension | Current score | Readiness judgment |
| --- | ---: | --- |
| Contribution and significance | 4/5 | Publication-worthy evaluation question |
| Technical soundness | 4/5 | Sound for descriptive chart-process claims after R2-R2 is fixed |
| Evidence and clinical validity | 4/5 | Appropriately bounded; clinician interpretation remains a human gate |
| Claim discipline and responsible research | 4/5 | Strong prose boundary; figure terminology must match it |
| Clarity and organization | 4/5 | Professional, readable, and non-defensive |
| Positioning and related work | 3/5 | Adequate for review after a modest closest-work expansion |
| Reproducibility and auditability | 4/5 | Strong local package; immutable release and supplementary configuration pending |

**Absolute stance:** Minor revision; scientifically viable but not yet submission-ready.  
**Confidence:** High for internal consistency and claim-boundary assessment. Moderate for field-wide novelty because no new external search was performed in this follow-up.

## Remaining scientific blockers

The following must be corrected before the manuscript should be sent to a journal:

1. Align Figure 1 and Figure 3 terminology with the narrowed manuscript claims.
2. Resolve the contradiction between a non-90%-valid finite-draw interval and reporting “90% coverage error” against 0.90.
3. Package the complete variable-level analysis with units and aggregation definitions, and correct the contradictory limitation statement.
4. Add the missing implementation configuration to the supplement.

The related-work expansion is strongly recommended but is less decisive than the four items above. I do not require a new architecture, additional cohort, matched observed-chart constraint analysis, or full 100-draw five-seed rerun for the current bounded paper. Those would strengthen future work rather than rescue an unsupported central claim.

## Human submission gates

These remain outside what code or manuscript editing alone can resolve:

- A clinician or clinical physiologist must review the chart-state constraints, asynchronous carry-forward interpretation, variable-level errors, and clinical terminology.
- A statistician or probabilistic-forecasting expert should confirm the final finite-draw interval and coverage wording.
- The companion scoping review requires qualified human dual verification and authenticated literature-database updating before it can support a stronger novelty claim.
- The research team must confirm the institutional ethics determination.
- Authors, corresponding author, funding, competing interests, and CRediT contributions must be finalized.
- All authors must verify the generated results, references, AI-use statement, and final manuscript.
- A stable, immutable, reviewer-accessible code and artifact repository must replace local workspace paths.

## Final recommendation

**Minor revision.**

The scientific core is now publishable in principle. The revision succeeds because it narrows the claim to what the data and frozen experiments actually establish rather than trying to defend a broader medical-world-model claim. Once the figure terminology, finite-draw coverage labeling, supplementary variable table, and implementation details are corrected, the remaining barriers are primarily human validation and submission governance.
