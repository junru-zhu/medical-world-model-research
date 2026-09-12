# Original Research Paper Pre-Results Audit

Audit date: 12 September 2026  
Manuscript: *Beyond One-Step Error: Calibrated Free-Running Evaluation of ICU
World Models Across Hospital Systems*  
Review stage: methods and implementation, before five-seed result freeze  
Recommendation at review: major revision

## Independent perspectives

One reviewer audited scientific software, rollout semantics, leakage,
calibration, support, and metric implementation. A second reviewer audited
estimands, seed aggregation, bootstrap inference, rank stability, external
validation, table design, and manuscript-code consistency.

Neither reviewer interpreted the incomplete seed matrix as a final scientific
result.

## Checks that passed

- No patient overlap across training, validation, internal-test,
  external-calibration, or external-test partitions.
- Preprocessing statistics and variable selection use cohort-A training data
  only.
- Deterministic, ridge, and neural publication comparisons use the same
  24-hour-eligible anchors and six-hour stride.
- Forecast anchor indexing and target offsets are correct.
- The cached Transformer rollout agrees numerically with full causal
  attention.
- The manuscript maintains a passive-forecasting boundary and does not convert
  action-free data into causal or policy claims.

## Findings and revision status

| ID | Finding | Status |
| --- | --- | --- |
| O-01 | Raw and recalibrated external evaluations consumed different Monte Carlo streams, so point errors were not invariant | Corrected in code with deterministic split-specific streams; stale artifacts must be regenerated and the final analyzer enforces patient-level NMAE and mask-Brier invariance |
| O-02 | Physiological constraints were computed on all decoder emissions rather than the actual mask-gated rollout state | Corrected: rollout-state violations are primary and decoder-emission violations are a separately labeled diagnostic; stale artifacts must be regenerated |
| O-03 | The lightweight matrix summarizer could accept stale or cross-wired files | Corrected: status, model, seed, checkpoint, stream policy, constraint policy, horizons, stride, support, trajectory count, and calibration split are validated |
| O-04 | Research hypotheses and primary estimands were insufficiently defined | Corrected through `experiments/frozen-analysis-specification.md`; questions are estimation focused and the averaging order and formulas are explicit |
| O-05 | Seed resampling implied an unsupported training-randomness estimand | Corrected: neural predictions are averaged over the five fixed instances, patients are bootstrapped, and seed SD/range are descriptive |
| O-06 | The inspected implementation seed weakened prospective interpretation | Corrected analytically: all seed-20260912 evaluation artifacts will be regenerated under the final pipeline and a four-seed exclusion sensitivity is mandatory |
| O-07 | Rank-reversal frequency was promised but not implemented, and cross-site output columns were mislabeled | Corrected: the analyzer reports Spearman correlation and pairwise reversal fraction with explicit cross-horizon and cross-site schemas |
| O-08 | Rollout-degradation area and cross-cohort uncertainty were not implemented | Corrected: normalized trapezoidal rollout area and independent-cohort patient bootstrap for 12-hour NMAE are generated |
| O-09 | Recalibration language exceeded the implemented horizon-wise pooled spread scaling | Corrected: the analysis is post-pilot, adaptation assisted, marginal, and target weighted; width, CRPS, moment-matched Gaussian score, and coverage are reported together |
| O-10 | “NLL” could be mistaken for an exact rollout likelihood | Corrected terminology: moment-matched Gaussian negative log score, with a 20/50/100-trajectory numerical sensitivity planned |
| O-11 | External and internal cohorts were described as paired | Corrected: different patients are resampled independently; only within-cohort model contrasts are patient paired |
| O-12 | Architecture size and dropout descriptions did not match implementation | Corrected: parameter counts are unmatched, dropout is Transformer only, and claims are model-family comparisons rather than mechanistic ablations |
| O-13 | Training and validation loss reports average minibatch objectives | Disclosed; model selection remains cohort-A validation only, while publication metrics use patient-macro aggregation |

## Remaining audit gates

1. complete the corrected five-seed matrix;
2. regenerate every stale seed-20260912 evaluation and calibration artifact;
3. run both matrix summarizers and require technical completeness;
4. run the Monte Carlo sample-count sensitivity;
5. freeze tables and figures from generated files only;
6. conduct a new independent results-and-claims review;
7. obtain clinical and author-level review before submission.

## Current interpretation

The design is technically recoverable and the major implementation defects
were found before final result freeze. No first-seed recalibration or
physiological-constraint number produced by the superseded evaluator may be
used in the manuscript.
