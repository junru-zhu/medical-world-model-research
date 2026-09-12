# Independent Reviewer 1 Follow-up Report

## Reviewer perspective

Statistics, experimental design, and reproducibility.

## Overall assessment

This revision has addressed the decisive concerns from my first review. Most
importantly, the manuscript no longer asks the 20-trajectory empirical
interval to establish calibration of the underlying infinite-draw predictive
distribution. It now defines the quantile construction, gives the expected
finite-sample coverage at 20, 50, and 100 draws, describes spread adaptation as
an operational adjustment to the finite-draw procedure, and states that the
Monte Carlo sensitivity demonstrates trajectory-count dependence rather than
convergence. That is an appropriate resolution. I do not require a new
high-trajectory analysis or a claim of underlying-distribution calibration for
the paper in its present, narrowed form.

The other previously decisive reporting omissions have also been repaired.
The manuscript or supplement now reports the prespecified rollout-area
results, horizon-specific scored-patient and observed-target support, the
implementation-seed exclusion sensitivity, the conditional interpretation of
the patient bootstrap, and the fixed-budget nature of the model comparison.
The claim boundary has been narrowed from general physiological validity to
recorded chart-process forecasting and prespecified chart-state diagnostics.

I independently rechecked the principal revised claims against the frozen
analysis summary, Monte Carlo summary, variable-level CSV, validation JSON,
supplement, and regenerated figures. I did not find a new material numerical
contradiction in the reported main results. The paper now has a scientifically
defensible core. A small number of package and reporting inconsistencies should
still be corrected before submission.

## Resolution of the prior decisive concerns

### 1. Finite-trajectory coverage interpretation: resolved

The revised Methods explicitly state that linearly interpolated empirical 5th
and 95th percentiles from 20 draws have expected coverage of approximately
0.814, rather than 0.90, under exchangeability with a calibrated continuous
distribution. The manuscript also states that these estimates do not directly
characterize the infinite-draw model distribution. The abstract, Results,
Discussion, and Figure 3 caption consistently frame the analysis as
finite-draw uncertainty and spread adaptation.

This is the key correction. The state-space model's underdispersion remains
supported because its coverage is approximately 0.50 under both the 20-draw
primary analysis and the 100-draw sensitivity, far below either the nominal
target or the relevant finite-draw expectation. For GRU-D and the Transformer,
the manuscript now appropriately emphasizes trajectory-count dependence
rather than using their 20-draw coverage as direct evidence of underlying
distributional miscalibration.

The label “12 h 90% coverage error” in the main descriptive table is still
slightly easy to overread. It would be clearer as “absolute deviation from
0.90, 20-draw interval,” but the surrounding Methods and Discussion now make
the intended estimand clear.

### 2. Monte Carlo sensitivity: resolved for the narrowed claim

The revised manuscript identifies the sensitivity as using one trained seed,
a fixed 1,000-patient subset, separate fixed streams, and no repeated-stream
Monte Carlo intervals. It describes the result as a limited trajectory-count
sensitivity and explicitly says that it demonstrates dependence rather than
convergence.

That is sufficient for the current paper. Repeated nested streams would be
needed for a convergence claim, but the manuscript no longer makes that
claim. Additional Monte Carlo computation would strengthen the study but is
not a prerequisite for the present finite-draw conclusions.

### 3. Prespecified rollout-area outcome: resolved

The revised reporting restores the external rollout-area results. The values
agree with the frozen analysis: Transformer 0.5083, GRU-D 0.5087, ridge
0.5158, last observation carried forward 0.5516, state-space model 0.6105,
hourly median 0.6652, and global median 0.6656, with neural seed variation
reported where applicable. The prior selective-reporting concern is resolved.

### 4. Common support and changing effective support: resolved

The manuscript now distinguishes common anchor eligibility from
horizon-specific scored-patient and observed-target support. Supplementary
Table S2 reports the relevant counts, including the change from 1,810 to 1,773
scored patients internally and from 10,245 to 10,162 externally between one
and 24 hours. The text no longer implies that every horizon has an identical
effective target population.

An intersection-of-horizons sensitivity could still be informative, but it is
not required once the estimand and changing support are disclosed accurately.

### 5. Bootstrap and seed uncertainty: resolved

The revised Methods and figure captions distinguish patient-bootstrap
intervals conditional on five fixed fitted instances from across-seed
standard deviations. The captions also identify seed ranges where used.
These uncertainty sources are no longer presented as interchangeable.

The constraint rates remain descriptive pooled-state diagnostics without
patient-clustered intervals or a matched observed-chart reference. The revised
manuscript now gives those caveats and avoids population-level or clinical
validity claims.

### 6. Implementation-seed exclusion: resolved

Supplementary Table S3 reports the promised exclusion analysis. The stated
external 12-hour NMAE values—0.5216 for GRU-D, 0.5213 for the Transformer, and
0.6234 for the state-space model—agree with the frozen artifact. The ranking
and the state-space underdispersion conclusion do not depend on retaining the
inspected implementation seed.

### 7. Unequal model selection and training budget: resolved by claim narrowing

The manuscript now describes the comparisons as fixed-budget benchmarks of
specific implementations, discloses unmatched parameter counts and different
validation-selection objectives, and notes that all GRU-D and Transformer
runs selected the maximum epoch. It does not present the results as controlled
architecture ablations or population-level model-family rankings.

Longer training and harmonized model selection would be necessary for a
strong architecture-superiority claim. They are not necessary for the revised
benchmark claim.

### 8. Variable-level reporting: substantially resolved, with one package issue

The newly generated variable-level CSV contains all 24 variables for all seven
models, and the selected original-unit MAE values in the manuscript and
Supplementary Table S1 agree with that artifact. Reporting original-unit
errors is a useful addition, and the authors correctly avoid assigning a
minimum clinically important difference.

The supplement itself, however, displays only 10 variables while referring to
a local repository path for the complete 24-variable table. This is not a
self-contained supplementary table for a reader or reviewer. It should either
include all 24 variables or be retitled as a clearly defined selected-variable
table, explain the selection rule, and attach the complete CSV as a formal
supplementary data file. The supplement should also state that these
variable-level MAEs pool observed targets rather than using the patient-macro
aggregation of the primary NMAE. Counts should remain visible because several
variables are sparse at 12 hours—for example, HCO3 has 48 observed targets,
BaseExcess 59, and Chloride 142.

## Remaining scientific and technical issues before submission

I do not identify a remaining scientific blocker that requires new model
training, a new dataset, or an underlying-distribution calibration analysis.
The following narrower issues should nevertheless be fixed before the package
is submitted.

1. **Make Figure 1 consistent with the revised claim boundary.** The current
   regenerated Figure 1 still labels its evidence boxes “Uncertainty
   calibration” and “Physiological validity.” These labels are broader than
   the manuscript's now-careful claims. They should be replaced with language
   such as “Finite-draw uncertainty” and “Chart-state constraint diagnostics,”
   and the source figure should be regenerated.

2. **Correct stale figure-contract language.** The figure contract still uses
   “recalibrated,” “physiological validity,” and a claim that 20 trajectories
   are numerically stable enough. These descriptions conflict with the revised
   manuscript. Although the contracts may be internal documentation, leaving
   them stale creates an avoidable reproducibility and future-regeneration
   risk.

3. **Complete or explicitly delimit Supplementary Table S1.** Provide the full
   24-variable table as a submission artifact, or clearly label the displayed
   10-variable subset and document its selection rule. State the aggregation
   method and retain variable-specific observed-target counts.

4. **Fix the contradictory limitation sentence.** The Limitations section says
   that “Variable-level clinical-unit results were not developed,” although
   such results are now presented. The intended limitation appears to be that
   no clinically validated utility threshold or minimum clinically important
   difference was developed.

5. **Rerun final figure QA after the last render.** The final figure PDFs and
   SVGs were regenerated after the recorded collision-audit JSON files. The
   alignment records are current and pass, and visual inspection did not reveal
   a serious layout problem, but the collision/text audits do not certify the
   final files because they predate them. Final QA should be rerun on the exact
   submitted figures.

6. **Treat the package validator as a limited check.** I reran the supplied
   validator and reproduced
   `technical_pass_submission_gates_pending`. That result verifies selected
   manuscript phrases, references, counts, and high-level analysis statuses.
   The script does not currently validate the supplement, variable-level
   table, figure text, figure-audit freshness, or hashes linking the manuscript
   to the exact frozen artifacts. The technical-pass label should not be
   interpreted as a complete submission audit.

7. **Finalize an immutable reproducibility release.** A stable code and
   artifact repository remains pending in the validation JSON. The release
   should include the supplement and full variable-level data, exact figure
   source data, environment and execution instructions, and hashes or version
   identifiers for the analyzed outputs.

## Human and institutional submission gates

The following are not machine-fixable scientific-analysis issues and should
remain explicit human gates:

1. Clinical-domain review of the selected chart-state constraints, terminology,
   and the limits of their clinical interpretation.
2. Institutional confirmation of the applicable ethics determination.
3. Final authorship, affiliations, corresponding-author details, funding,
   competing interests, and CRediT contributions.
4. Human verification of the scoping-review characterization, citations, and
   generative-AI disclosure.
5. Final author sign-off that the immutable release and submitted figures
   correspond to the frozen analysis.
6. Completion of any additional independent or venue-specific review required
   by the research group. This report completes the requested Reviewer 1
   statistical follow-up; it does not replace clinical or institutional
   review.

## Recommendation

**Minor revision; scientifically acceptable after the targeted reporting,
figure-language, and final-package corrections above.**

The prior major statistical objection has been resolved appropriately through
claim narrowing and transparent finite-draw reporting. I would not make
acceptance conditional on demonstrating calibration of the underlying
infinite-draw distribution. Once the visible claim-language inconsistencies,
supplement completeness, final figure QA, and reproducibility release are
addressed, I see no remaining statistical or experimental-design reason to
block submission.
