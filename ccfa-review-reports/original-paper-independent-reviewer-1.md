# Independent Reviewer 1 Report

## Manuscript

**Beyond One-Step Error: Calibrated Free-Running Evaluation of ICU World Models Across Hospital Systems**

## Reviewer perspective

Statistics, experimental design, and reproducibility.

## Overall assessment

This is a thoughtful and unusually transparent benchmark study. The authors preserve the distinction between passive forecasting and causal or clinical claims, use patient-disjoint development and external partitions, evaluate all models on a common anchor construction, retain negative findings, and provide unusually detailed frozen analysis artifacts. I independently checked the principal numerical statements in the abstract, Results, tables, and figures against `experiments/results/frozen-analysis/publication-summary.md`, the underlying frozen CSVs, and the Monte Carlo sensitivity files. I found the headline values to be accurately transcribed. In particular, the external NMAE values, frozen 12-hour contrasts, cross-cohort degradation intervals, recalibration results, constraint rates, and rank summaries agree with the frozen outputs.

The paper is not ready for submission in its current form, however. The central statistical problem is that the manuscript interprets coverage from only 20 empirical trajectories as if it were directly comparable with nominal 90% predictive coverage. With the implemented linearly interpolated 5th and 95th sample quantiles, finite Monte Carlo sampling itself induces substantial undercoverage, even for draws from a perfectly calibrated continuous predictive distribution. The authors' own sensitivity experiment demonstrates that this is not a small effect. Consequently, part of the reported raw “miscalibration,” and part of what external spread scaling repairs, is an artifact of the interval estimator rather than evidence about the underlying predictive distribution. This issue reaches the title, abstract, main calibration claims, and interpretation of recalibration.

There are also important reporting and design issues: a protocol-defined primary rollout-area estimand is calculated but omitted from the manuscript; the promised pilot-seed exclusion sensitivity is not reported; effective scored-patient support changes across horizons despite common anchor eligibility; and model comparisons mix different validation-selection criteria and apparently unfinished neural training trajectories. These problems are addressable, but they require major revision and, for the calibration claim, preferably additional computation.

## Main strengths

1. **Strong leakage controls and data separation.** Cohort A is used for fitting and selection, cohort B is partitioned into external calibration and frozen testing, and the manuscript reports zero-shot and adapted results separately. I found no evidence in the supplied artifacts that external-test outcomes were used for model or hyperparameter selection.

2. **Appropriate clustering unit for the reported NMAE intervals.** Repeated anchors are kept within patients, and the paired and cross-cohort bootstraps resample patients rather than treating anchors or observed targets as independent.

3. **Good provenance and amendment practice.** The common-support correction, implementation-seed chronology, recalibration procedure, random-stream correction, and constraint-state correction are explicitly recorded rather than silently overwritten.

4. **Negative results are preserved.** The state-space model's poor accuracy and dispersion, the near tie between GRU-D and the Transformer, and the stability of cross-site rankings are reported rather than reframed as successes.

5. **Claims are generally bounded appropriately.** The paper repeatedly states that passive forecasting does not establish treatment effects, counterfactual validity, policy quality, clinical benefit, or deployment safety.

6. **Figures are legible and numerically consistent.** The supplied collision and alignment audits pass, and visual inspection did not reveal a plotted value that contradicts the frozen tables.

## Major concerns

### 1. The 20-trajectory coverage analysis confounds model calibration with finite-sample interval construction

The evaluator constructs a “90% interval” using `torch.quantile(samples, 0.05)` and `torch.quantile(samples, 0.95)` from 20 trajectories. This estimator is not expected to achieve 90% coverage when the target and trajectories are exchangeable draws from a perfectly calibrated continuous distribution. Under the corresponding uniform probability-integral-transform argument, the expected coverage of the linearly interpolated interval is only about 81.4% for 20 samples, about 86.5% for 50 samples, and about 88.2% for 100 samples. Thus, comparing the 20-sample interval directly with 0.90 builds substantial numerical undercoverage into the metric.

The observed sensitivity is consistent with this concern. At 12 hours, coverage rises from 0.8401 to 0.8945 for GRU-D and from 0.8632 to 0.9195 for the Transformer when the trajectory count increases from 20 to 100. Their point NMAE, CRPS, interval width, and Gaussian score also move materially. This is not merely “coarse quantiles”; it changes the substantive calibration interpretation. The pooled spread multiplier is fitted from 20-sample means and standard deviations, so it compensates for both model dispersion and finite-sample estimation. The current abstract statement that recalibration reduced coverage error, and the title's use of “Calibrated,” do not make this distinction prominent enough.

I recommend one of the following before submission:

- rerun the primary probabilistic evaluation and recalibration with a substantially larger trajectory count and demonstrate convergence across repeated Monte Carlo streams;
- use a finite-sample-valid order-statistic prediction interval and clearly define its nominal coverage; or
- substantially narrow the claim to calibration of the *20-draw empirical forecast procedure*, not calibration of the underlying learned predictive distribution.

At minimum, the Methods must define the quantile interpolation rule, the abstract must disclose the trajectory-count dependence, and the Discussion must state that the recalibration multiplier is not identifiable as a pure model-calibration correction. The Gaussian negative log score also uses a 20-sample standard deviation and is therefore affected by the same finite-sample issue.

### 2. The Monte Carlo sensitivity is informative but not a full convergence study

The sensitivity uses one inspected training seed, one fixed 1,000-patient subset, and one random stream for each trajectory count. The runs are not documented as nested trajectories for every patient, and no repeated Monte Carlo streams quantify simulation variability at a fixed count. Therefore, the plotted 20-to-50-to-100 changes combine trajectory-count effects with stream-specific variation.

The Extended Data figure should not be described as establishing that the 20-trajectory budget is “stable enough.” It shows the opposite for coverage and nontrivial movement for NMAE, CRPS, width, and Gaussian score. Repeating the sensitivity over several evaluation streams, preferably using nested draws, would allow the authors to estimate Monte Carlo standard error and choose a defensible primary trajectory count.

### 3. A protocol-defined primary outcome is omitted from the Results

Section 2.8 lists normalized area under the 1-to-24-hour rollout-degradation curve as a primary descriptive outcome. The analyzer generated `rollout-area.csv`, but the manuscript does not report these values in the Results, table, supplement, or figure caption. This is a selective-reporting problem even though the horizon curves themselves are shown.

For reference, the frozen zero-shot external NMAE rollout-area means are approximately 0.5158 for ridge, 0.5087 for GRU-D, 0.5083 for the Transformer, and 0.6105 for the state-space model. The manuscript should report the complete protocol-defined rollout-area results, including the deterministic baselines and seed variation where applicable, or provide a dated amendment explaining why this primary estimand was removed.

### 4. “Common support” does not produce identical effective patient support across horizons

The anchor eligibility rule is common across horizons, but value outcomes are scored only where a target is observed. Consequently, the effective patient set changes with horizon. The frozen support file reports 1,810 internal patients at one hour and 1,773 at 24 hours; externally, the corresponding counts are 10,245 and 10,162. At 12 hours, the paired contrasts use 1,806 internal and 10,178 external patients, not all 1,841 and 10,622 patients with at least one eligible anchor.

The manuscript currently says that the common-support rule prevents estimates from being calculated on a different patient-time population and promises that final tables “will additionally report” target counts. That statement is too strong and the promised reporting is absent. Please distinguish:

- common *anchor eligibility*;
- horizon-specific observed-target support; and
- the patient set entering each patient-macro estimate.

A useful sensitivity would restrict cross-horizon comparisons to patients with at least one observed target at every reported horizon. At minimum, add patient and observed-target counts by horizon and soften the population-equivalence claim.

### 5. The uncertainty intervals condition on five fixed trained instances

The paired bootstrap first averages each neural model over five fixed seeds and then resamples patients. These intervals quantify patient-population sampling conditional on the selected trained instances; they do not include uncertainty over model training. The manuscript explains this in the Methods, which is good, but the abstract and Results call them simply “95% bootstrap intervals.” For small contrasts, especially GRU-D versus Transformer, this can be mistaken for total uncertainty.

Please label these intervals explicitly as patient-bootstrap intervals conditional on the five fixed instances wherever they are central to interpretation. Across-seed standard deviations should remain separate and should not be visually or verbally treated as confidence intervals.

Constraint rates require an additional caveat. They are pooled over trajectory states, so patients with more eligible anchors contribute more weight, and no patient-bootstrap intervals are available. Statements such as “demonstrates” physiological failure should be recast as descriptive findings from the evaluated runs rather than patient-population inference.

### 6. The promised implementation-seed exclusion sensitivity is not reported

Section 2.9 says that a sensitivity analysis excludes the inspected implementation seed. The frozen files contain that analysis, and it appears reassuring: the main patterns remain stable. For example, the external 12-hour NMAE values excluding seed 20260912 are 0.5216 for GRU-D, 0.5213 for the Transformer, and 0.6234 for the state-space model. However, none of these results appears in the manuscript.

Because inspection of the first seed motivated or formalized parts of the analysis, the exclusion result should be reported in the Results or supplement, not only generated in a local CSV.

### 7. Model-family comparisons are affected by unequal selection criteria and incomplete training convergence

Ridge regularization is selected using validation 12-hour patient-macro NMAE, whereas neural checkpoints are selected using a teacher-forced minibatch objective combining Gaussian NLL, mask cross-entropy, and, for the state-space model, KL loss. This is not a common validation criterion. In addition, every GRU-D and Transformer run has its best epoch at the maximum permitted epoch 20, suggesting that the training budget, rather than an early-stopping optimum, determined the selected checkpoints. Parameter counts also range from 59,232 to 247,848.

The manuscript acknowledges unequal parameter counts and avoids a mechanistic architecture claim, but the comparison still should be described as a fixed-budget benchmark of particular implementations, not a robust ranking of model families. Ideally, the authors should provide training curves and a longer-training sensitivity for GRU-D and the Transformer, and either select all model families using a common validation estimand or justify why different selection objectives are scientifically appropriate. Without this, statements that a family is “strongest” should remain narrowly tied to the frozen implementation.

### 8. Reproducibility remains prospective rather than independently executable

The local artifacts are detailed, but the Data and Code Availability statement is future tense, and the submission validator still marks the stable code and artifact repository as pending. The manuscript also omits several implementation details that materially affect replication, including:

- the exact NMAE equation and the order of patient, anchor, and variable aggregation;
- empirical quantile interpolation;
- CRPS estimator form;
- Gaussian scale bounds;
- mask-loss and KL weights;
- early-stopping patience;
- ridge regularization candidate grid;
- the precise stochastic mask-feedback procedure; and
- the accelerator/software environment needed to interpret residual nondeterminism.

These details exist in code or checkpoint metadata but should be stated in the manuscript or a stable supplement. A public or otherwise reviewer-accessible immutable repository, environment lock file, execution commands, hashes, and source data for every figure are required before the reproducibility claim is complete.

## Additional issues

1. **Physiological validity is broader than the implemented checks.** The study evaluates pressure ordering and three simple bounds. These are useful diagnostics, but they do not establish physiological validity or coherence in a general sense. Consider renaming Section 3.5 and Figure 4 to “prespecified physiological constraint diagnostics” and narrowing the abstract and conclusion accordingly.

2. **Figure uncertainty encodings need fuller captions.** Figure 2a and Figure 4a-b use ribbons representing one across-seed standard deviation, but their manuscript captions do not define the ribbons. Figure 2d displays seed ranges, not confidence intervals. Extended Data Figure 1 should state prominently that it uses one training seed and no repeated Monte Carlo streams.

3. **The observation-mask conclusion should be horizon-specific.** Section 3.4 states that the state-space model had the weakest observation-process forecast “within each cohort,” but the reported numbers are specifically 12-hour values. Please add that qualifier unless the all-horizon statement is explicitly documented.

4. **The manuscript still contains prospective wording.** Section 3.1 says final tables “will additionally report” observed-target counts, and the availability statement says the package “will contain” artifacts. A complete scientific draft should either include these materials or state precisely what is currently available.

5. **Protocol status is stale.** `experiments/protocol.md` still says the five-seed matrix is in progress and retains TBD result tables. Preserving the original protocol is valuable, but it should be clearly labeled as a frozen historical document and accompanied by a final study-status record so that readers do not confuse provenance with current completeness.

## Questions for the authors

1. Will the authors rerun the principal probabilistic analysis with a trajectory count chosen from a repeated-stream convergence analysis, or will they redefine coverage using a finite-sample-valid interval?

2. Are the 20-, 50-, and 100-trajectory sensitivity runs nested at the patient-trajectory level? If not, can they be repeated with nested draws and multiple evaluation seeds?

3. Why was rollout-area, a declared primary outcome, omitted from the manuscript despite being calculated?

4. How sensitive are cross-horizon rankings to restricting the analysis to the intersection of patients with observed targets at all horizons?

5. Why was ridge tuned on 12-hour NMAE while neural models were checkpointed on a different one-step training objective? Would a common validation target alter the ranking?

6. Did GRU-D and Transformer validation loss continue to improve at epoch 20, and what happens under a longer training budget?

## Required revisions before submission

### Machine-fixable scientific and reporting issues

1. Correct or rerun the finite-trajectory coverage and recalibration analysis; revise the title, abstract, figures, and Discussion to match what is actually calibrated.
2. Strengthen the Monte Carlo study with repeated or nested streams, or explicitly present it as a limited single-stream sensitivity.
3. Report all protocol-defined primary outcomes, especially rollout area.
4. Report horizon-specific patient and observed-target support and qualify the common-support claim.
5. Report the implementation-seed exclusion sensitivity.
6. Clarify the three distinct uncertainty sources: patient sampling, training-seed variation, and evaluation Monte Carlo variation.
7. Add training-convergence evidence and address the unequal model-selection criteria, or narrow the comparative claims.
8. Complete figure captions and reproducibility methods; remove prospective placeholder wording.
9. Create and verify a stable, immutable code/artifact release with exact environment and execution instructions.

### Human or institutional submission gates

1. Clinical-domain review of the physiological constraints, terminology, and interpretation.
2. Institutional confirmation of the applicable ethics or exempt/non-human-subjects determination.
3. Final author list, affiliations, corresponding author, funding, competing interests, and CRediT contributions.
4. Author verification of all analyses, references, and the generative-AI disclosure.
5. Completion of the planned independent results-and-claims review process; this report constitutes one statistics/design review, not the clinical review.

## Recommendation

**Major revision; submission blocked until the statistical calibration issue and selective primary-outcome reporting are resolved.**

The study has a publishable core and unusually strong auditability. My recommendation is driven less by numerical inconsistency than by interpretation: the current 20-trajectory interval procedure makes the central calibration conclusion materially ambiguous. Once that issue is corrected, the omitted prespecified results are restored, and the reproducibility and human submission gates are completed, the paper could make a useful methodological contribution.
