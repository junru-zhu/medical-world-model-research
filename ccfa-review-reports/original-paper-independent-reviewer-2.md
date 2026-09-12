# Independent Reviewer 2 Report: Clinical Validity, Claim Boundary, and Publication Quality

**Manuscript:** *Beyond One-Step Error: Calibrated Free-Running Evaluation of ICU World Models Across Hospital Systems*  
**Review date:** 12 September 2026  
**Review mode:** Full scientific and writing review  
**Target venue:** Not specified; assessed against a general medical-AI or clinical-informatics journal standard  
**Materials inspected:** `manuscript/original-paper.md`; all five final original-paper figures; the frozen five-seed publication summary and supporting result tables; Monte Carlo sensitivity results; protocol and amendment records; implementation details relevant to rollout, calibration, masks, and constraints; and the companion scoping review  

## Overall assessment

This is a thoughtful and unusually transparent evaluation paper. The strongest contribution is not a new architecture. It is the demonstration that one-hour error, long-horizon error, predictive spread, observation-mask behavior, and simple state constraints can rank the same model families differently. The frozen results support that descriptive conclusion. The passive-forecasting boundary is also handled responsibly: the manuscript does not convert an action-free observational dataset into treatment, counterfactual, policy, or clinical-benefit claims.

I nevertheless recommend **major revision before submission**. The paper's central calibration evidence remains materially dependent on using only 20 rollout trajectories, and the one completed sensitivity analysis shows that coverage, CRPS, and even the Monte Carlo point estimate change appreciably at 50 and 100 trajectories. In addition, the terms “physiological validity,” “physiological coherence,” and “safety-relevant conclusions” are too strong for four elementary chart-state constraints that lack a real-data reference rate and may combine measurements carried forward from different times. These are repairable problems, but they affect the paper's headline interpretation rather than only its presentation.

## Main strengths

1. **The evaluation question is important and clearly motivated.** The manuscript correctly distinguishes a single generated step from a free-running trajectory whose outputs become later inputs. The common 24-hour support set avoids a common but serious horizon-comparison bias.

2. **The data split and adaptation boundary are credible.** Cohort-A development, patient-disjoint internal testing, a separate cohort-B calibration partition, and a frozen cohort-B test partition are clearly separated. Zero-shot and recalibrated results are not conflated.

3. **Negative findings are retained.** Ridge wins at one hour, the GRU-D-style model and Transformer are nearly tied at longer horizons, the state-space model performs poorly despite explicit latent stochasticity, and external ranking is more stable than originally hypothesized. This gives the paper a scientific rather than promotional tone.

4. **The causal boundary is appropriate.** The manuscript repeatedly and correctly limits the evidence to passive forecasting under the observed measurement process. Figure 1 makes the non-identified treatment, counterfactual, policy, benefit, and deployment claims visible.

5. **The figures and tables are technically polished.** All five figures are legible, internally consistent with the frozen result files, and free of detected alignment or collision failures. Figures 2 and 3 communicate the main accuracy and uncertainty findings particularly well.

6. **The audit trail is strong.** The seed chronology, common-support correction, Monte Carlo stream correction, constraint-state correction, unmatched parameter counts, and post-pilot analyses are disclosed rather than hidden.

## Major concerns

### R2-M1 — The headline calibration result is confounded by Monte Carlo sample count

**Location:** Abstract Results and Conclusions; Methods 2.7 and 2.9; Results 3.3 and 3.6; Discussion paragraphs 2 and 5; Figure 3.

The primary analysis estimates a 90% interval, CRPS, rollout mean, and Gaussian score from only 20 trajectories per anchor. The post-analysis sensitivity is not a minor numerical check: on the same 1,000 external patients, 12-hour GRU-D coverage changes from 0.8401 at 20 samples to 0.8945 at 100, and Transformer coverage changes from 0.8632 to 0.9195. CRPS and sample-mean NMAE also improve as the trajectory count increases. Thus, for GRU-D and the Transformer, much of the apparent raw undercoverage and part of the apparent benefit of spread scaling may reflect finite-sample estimation of the empirical rollout distribution rather than model miscalibration alone.

The manuscript acknowledges this in Results 3.6 and the Discussion, but the abstract still presents the reduction in coverage error as a central calibration result without the qualification. The title also foregrounds “Calibrated” evaluation. The RSSM underdispersion is robust to the sensitivity analysis, but the same strength of conclusion is not justified for the other two neural models.

**Required change:** Either rerun the primary probabilistic evaluation on the full support set and all five seeds with a trajectory count shown to be adequate, or narrow the central claim to evaluation of a 20-sample empirical rollout distribution. A practical repair would use at least 100 trajectories for coverage and proper-score reporting, retain 20 trajectories only as a computational sensitivity point, and refit spread multipliers using the same final trajectory policy. If a full rerun is infeasible, the abstract, title, Figure 3 interpretation, and conclusion must state that the apparent calibration deficit and recalibration effect for GRU-D and the Transformer are partly Monte Carlo-count dependent.

### R2-M2 — “Physiological validity” and safety language exceed the implemented checks

**Location:** Abstract lines 39–47; Introduction lines 79–83; Figure 1 panel c; Methods 2.8; Results 3.5; Figure 4; Discussion lines 497–503; Conclusion.

The implemented checks are arterial-pressure ordering and bounds for O2Sat, SaO2, and FiO2. These are useful failure indicators, but they do not establish physiological validity. They also do not establish clinical safety. The manuscript's own amendment record states that change thresholds and multivariate conformity were deferred and that no broader physiological-validity claim should be made.

The pressure result requires additional clinical interpretation. The primary rate is measured after sampled masks are applied and unmeasured variables are carried forward. SBP, MAP, and DBP can therefore represent values last measured at different simulated times. A pressure-order violation in that state may reflect an incoherent observation-and-carry-forward process rather than an impossible simultaneous physiological state. Conversely, median baselines satisfy the relation by construction, which demonstrates why a low count is not a validity certificate. The paper currently has no observed-data reference rate, no comparator based on actual carried-forward chart states at matched anchors, and no clinical rationale for whether each listed violation has the same meaning.

**Required change:** Rename this evidence throughout as “prespecified constraint consistency,” “chart-state plausibility diagnostics,” or similarly bounded language. Remove “safety-relevant conclusions” unless the paper defines an explicit hazard and exposure model. Report matched real-data or observation-process reference rates, explain the asynchronous/carry-forward interpretation, and separate simultaneous decoder-emission consistency from mask-gated chart-state consistency. The conclusion should say that average error failed to predict these narrow constraint rates, not that the study established or refuted physiological validity.

### R2-M3 — The modeled object is an observed chart process, not a validated patient-state world model

**Location:** Title; Introduction lines 64–83; Methods 2.1, 2.4, 2.5, and 2.8; Discussion lines 518–523.

The models generate robust-scaled observed values and measurement masks, then carry unmeasured variables forward. Value outcomes are scored only where the real record contains a measurement. This is a reasonable joint model of an ICU charting process, but it is not a direct model of latent physiology. The observation policy is partly clinician- and workflow-driven, treatment actions are omitted, static variables are omitted, and discharge/death are not modeled as competing trajectory endpoints.

The manuscript generally recognizes this boundary, but “ICU world models,” “patient state,” and “physiological forecasting” can still invite a stronger interpretation than the task supports. In particular, favorable performance may reflect prediction of recorded measurements under an existing process of care rather than patient dynamics independent of that process.

**Required change:** Define the world-model object once and precisely as a passive model of recorded physiological observations and their acquisition process. Keep “world model” if the authors wish, but distinguish “chart-state rollout” from latent patient-state simulation in the title, abstract, and first Discussion paragraph. Explain how discharge, death, treatment, and unrecorded physiology limit the generated trajectory's meaning.

### R2-M4 — Aggregate NMAE establishes ranking, but not clinical importance

**Location:** Methods 2.8–2.9; Results 3.2 and Table 3.7; Discussion first paragraph.

The long-horizon difference between the Transformer or GRU-D and ridge is statistically precise under the fixed-instance patient bootstrap, but small in aggregate NMAE: approximately 0.009 at 12 hours externally. The paper does not translate this difference into original clinical units, show which variables drive it, or identify whether clinically important vital signs and sparse laboratory variables behave similarly. Patient-macro aggregation prevents patients with many anchors from dominating, but within a patient it still weights observed variable-time targets, so frequently measured variables contribute more than sparse ones.

The current evidence supports “lower aggregate normalized error,” not “clinically better dynamics.” This distinction matters because the paper uses a medical-world-model framing.

**Required change:** Add a compact variable-level analysis for clinically interpretable variables and report errors in original units or alongside clinically meaningful scales. At minimum, show whether the one-hour-to-long-horizon ranking change is shared across vital signs and laboratory variables rather than driven by a small subset. State that the study estimates predictive performance and does not define a minimal clinically important NMAE difference.

### R2-M5 — Inferential uncertainty is incomplete for several declared primary outcomes

**Location:** Methods 2.8–2.9; Results 3.3–3.5; Table 3.7; Figure 4.

The paper provides patient-bootstrap intervals for frozen 12-hour NMAE contrasts and cross-cohort degradation. Calibration, mask Brier, and constraint results are mainly accompanied by across-seed standard deviations. Across-seed variation is not a substitute for patient-clustered uncertainty, and five fixed seeds do not support a population-level architecture inference. The protocol originally promised patient-level bootstrap intervals for primary comparisons, whereas the final manuscript presents several primary outcomes descriptively without clearly calling out that narrowing.

The very large constraint differences are unlikely to disappear, but their uncertainty should still respect clustering by patient and repeated anchor. The manuscript should also avoid using the bootstrap intervals as if they covered the distribution of future training runs.

**Required change:** Add patient-clustered uncertainty for the main calibration, mask, and constraint comparisons, or explicitly designate them as descriptive estimates and record the protocol departure. Keep architecture statements scoped to the five trained instances under this training protocol. Report the number of ranked models for the Spearman analyses and avoid excessive precision for a seven-model rank calculation.

### R2-M6 — Publication positioning depends on a preliminary review and is otherwise too thin

**Location:** Introduction lines 72–77; References.

The novelty statement relies on the companion scoping review's finding that no primary study combined the selected evaluation features. That review is useful and carefully bounded, but its own manuscript states that qualified human dual verification, authenticated database updates, and expert content validation remain pending. The original paper currently has only eight references and no substantive related-work section covering probabilistic ICU forecasting, generative clinical time-series models, external validation, informative observation processes, or prior physiological-constraint evaluation.

**Required change:** Until the companion review passes its human verification gates, describe the gap as identified in a preliminary review rather than as settled field-wide absence. Add a focused related-work section that positions this benchmark against the closest clinical forecasting and generative trajectory studies, not only generic architecture and calibration references.

## Minor and presentation concerns

1. Results 3.1 says that “Final tables will additionally report observed-target counts by horizon,” but the final table does not do so. Replace this future-tense sentence and explain why 1,841/10,622 patients have eligible anchors while only 1,806/10,178 enter the 12-hour paired contrast.

2. Define NMAE explicitly in the manuscript as absolute error in training-IQR-scaled units. “Normalized” is otherwise under-specified.

3. Table 3.7 should label CRPS, coverage error, mask Brier, and pressure violations explicitly as 12-hour outcomes. It should also distinguish confidence intervals from across-seed standard deviations.

4. Figure 2's caption should explain the interval bars in panels b and c and the seed range in panel d. Figure 4 should state that heat-map color is violation frequency, not clinical severity.

5. Methods should report the mask-loss weight, KL weight, early-stopping patience, scale bounds, random-window training scheme, validation-window scheme, and exact checkpoint selection rule. These details exist in the implementation but are not recoverable from the paper alone.

6. The repeated causal and deployment disclaimers are scientifically appropriate, but they appear in the Abstract, Introduction, Methods, Figure 1, Discussion, Limitations, and Conclusion. Consolidating them would make the prose feel less audit-like while preserving the boundary.

7. “External,” “cross-site,” “cross-cohort,” and “across hospital systems” should be used consistently. The paper should state exactly what institutional distinction cohort A versus B represents and avoid implying prospective generalization.

8. The manuscript is readable and largely non-defensive. The main writing risk is procedural density: implementation-seed chronology and correction history interrupt the scientific narrative in several places. Keep essential departures in the main text and move the full audit ledger to the supplement.

## Claim-to-evidence judgment

| Central claim | Judgment |
| --- | --- |
| One-hour and long-horizon aggregate error need not select the same model | Supported by the frozen NMAE curves and paired 12-hour contrasts |
| GRU-D-style and Transformer performance is effectively tied externally at 12 hours | Supported for the five fixed trained instances; not an architecture-population equivalence claim |
| The RSSM is inaccurate and strongly underdispersed | Supported and robust to the trajectory-count sensitivity |
| Spread scaling changes uncertainty without changing point forecasts or rollout states | Supported by the recalibration invariant checks |
| GRU-D and Transformer are miscalibrated at the reported raw levels | Not fully supported because the estimated coverage changes materially with trajectory count |
| Accuracy does not imply satisfaction of the four implemented constraints | Supported |
| The constraints establish physiological validity or deployment safety | Not supported |
| Cohort transfer preserves model ranking while increasing aggregate error | Supported within these two challenge cohorts |
| The study supports causal, counterfactual, treatment, policy, benefit, or deployment claims | Correctly rejected by the manuscript |

## Ratings

| Dimension | Score | Basis and condition for improvement |
| --- | ---: | --- |
| Contribution and significance | 4/5 | Important evaluation problem and useful negative results |
| Technical soundness | 3/5 | Strong split and rollout design, but central uncertainty estimates are trajectory-count sensitive; improve with an adequate-sample primary rerun |
| Evidence and clinical validity | 3/5 | Ranking evidence is credible; clinical interpretation needs variable-level results and bounded constraint language |
| Claim discipline and responsible research | 4/5 | Causal boundary is strong; “physiological validity” and safety wording remain too broad |
| Clarity and organization | 4/5 | Professional and readable, with some audit-led procedural density |
| Positioning and related work | 2/5 | Too few close clinical references and dependence on a not-yet-human-verified review |
| Reproducibility and auditability | 4/5 | Excellent local artifact trail; several implementation details still need manuscript or supplement reporting |

**Reviewer confidence:** High. The manuscript, frozen tables, figures, protocol history, and relevant implementation paths were available and mutually checkable.

## Required revision priorities

| ID | Priority | Required revision |
| --- | --- | --- |
| R2-M1 | Decisive | Resolve trajectory-count dependence for the primary probabilistic results or substantially narrow the calibration claim |
| R2-M2 | Decisive | Replace physiological-validity/safety language with bounded constraint-consistency language and add a real-data reference |
| R2-M3 | High | Define the generated object as the recorded observation-and-mask process rather than latent patient physiology |
| R2-M4 | High | Add clinically interpretable variable-level performance and avoid implying clinical importance from aggregate NMAE |
| R2-M5 | High | Complete or explicitly narrow patient-clustered inference for non-NMAE primary outcomes |
| R2-M6 | High | Add close related work and qualify novelty until the companion review is human verified |

## Machine-fixable issues versus human submission gates

### Machine-fixable or analysis-team-fixable

- Run the higher-trajectory primary uncertainty analysis and regenerate calibration artifacts, tables, and Figure 3.
- Calculate matched observed-data and carried-forward reference constraint rates.
- Produce variable-level original-unit result tables.
- Add patient-clustered intervals for calibration, masks, and constraints.
- Correct stale support-count language, table headers, captions, terminology, and missing implementation details.
- Consolidate repeated disclaimers and move detailed chronology to the supplement.
- Expand the related-work section and qualify the preliminary novelty statement.

### Human submission gates

- A clinician or clinical physiologist must validate the meaning of the selected constraints, the asynchronous-measurement issue, and the clinical interpretation of variable-level errors.
- A qualified statistician or methods reviewer should approve the final Monte Carlo and clustered-uncertainty treatment.
- The companion scoping review requires qualified human dual verification, authenticated database updating, and expert validation before its absence claim can anchor novelty.
- The research team must complete the institutional ethics determination.
- Authors, corresponding author, funding, competing interests, and CRediT contributions must be finalized.
- All authors must verify the code-derived results, references, AI-use declaration, and final data/code release statement.

## Recommendation

**Major revision.**

The paper has a publishable core: a careful, real-data demonstration that rollout horizon and evaluation dimension alter conclusions about clinical dynamics models. I would support reconsideration after the calibration analysis is made numerically adequate, the constraint evidence is described at its true clinical strength, and the medical relevance is demonstrated beyond a single aggregate normalized error.
